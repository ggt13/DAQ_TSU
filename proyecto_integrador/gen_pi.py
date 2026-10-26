"""Proyecto integrador · Tu registro contra tu plan. Genera:

    PI_Colab_ALUMNO.ipynb   (repositorio)
    PI_Colab_PROF.ipynb     (sólo Drive: ejemplo resuelto y verificación de los CSV)

Uso:  python gen_pi.py            -> los dos cuadernos
      python gen_pi.py --prueba D -> además, versiones resueltas en D para ejecutarlas (las usa prueba_pi.py)

El alumno escribe su plan de adquisición y sus predicciones ANTES de ver el registro; luego carga un registro real
(un Govee H5075 en préstamo, datos de su área o una de las tres campañas RC-5 del grupo) y el cuaderno calcula la
calidad del registro, el filtro, la tendencia, el ciclo dominante y las alarmas con tiempo de confirmación e
histéresis. Termina con la tabla de lo predicho contra lo obtenido, su conclusión y su decisión, y un CSV firmado.

El registro de cada alumno es suyo y no se conoce de antemano: el cuaderno revisa que lo escrito esté completo y sea
coherente; lo correcto lo califica el profesor con el formato del proyecto.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import datos_pi as dp  # noqa: E402

SESION = "PI"
CARPETA = "proyecto_integrador"
ALUMNO = os.path.join(AQUI, "PI_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "PI_Colab_PROF.ipynb")
RAMA = os.environ.get("DAQ_RAMA", "main")
COLAB = cu.REPO + CARPETA + "/PI_Colab_ALUMNO.ipynb"
URL_DATOS = f"https://raw.githubusercontent.com/ggt13/DAQ_TSU/{RAMA}/{CARPETA}/datos/"

# Textos que escribe el alumno (entre comillas); lo demás son números
cu.TEXTOS |= {"VARIABLE", "UNIDAD", "SENTIDO", "FUENTE_REG", "ARCHIVO", "COLUMNA", "DECISION"}

DATOS_PI = f'URL_DATOS = "{URL_DATOS}"\n' + r'''
import io
import os
import urllib.request

import pandas as pd
from matplotlib.patches import Patch

FUENTES_REG = ("govee", "area", "campaña 1", "campaña 2", "campaña 3")


# ------------------------------------------------------------------------------------------- lectura del registro
AVISOS_LECTURA = []


def _tabla_cruda(ruta):
    """El archivo tal cual, sin suponer encabezados: Excel de ElitechLog, CSV de Govee o CSV de cualquier equipo.
    En un Excel con varias hojas se usa la que tiene más fechas."""
    if ruta.lower().endswith((".xls", ".xlsx")):
        hojas = pd.read_excel(ruta, header=None, dtype=str, sheet_name=None)
        return max(hojas.values(), key=lambda h: h.astype(str).apply(
            lambda c: c.str.contains(PATRON_FECHA, regex=True).sum()).max() if len(h) else 0)
    texto = open(ruta, encoding="utf-8-sig", errors="replace").read()
    lineas = [l for l in texto.splitlines() if l.strip()]
    # separador: el primero que aparece el mismo número de veces en los últimos renglones («;» antes que «,»,
    # porque con «;» la coma suele ser el punto decimal)
    cola = lineas[-50:]
    sep = next((c for c in (";", "\t", ",") if cola[0].count(c) > 0 and len({l.count(c) for l in cola}) == 1),
               max([",", ";", "\t"], key=lambda c: sum(l.count(c) for l in cola)))
    ancho = max(l.count(sep) for l in lineas) + 1
    return pd.read_csv(io.StringIO("\n".join(lineas)), sep=sep, header=None, names=range(ancho), dtype=str,
                       engine="python")


PATRON_FECHA = r"\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}"
PATRON_HORA = r"^\s*\d{1,2}:\d{2}"


def _a_numero(col):
    """Números escritos de cualquier manera: «23.4», «23,4», «23.4°C», «45 %», «1,013.2» (coma de miles)."""
    t = col.astype(str).str.strip()
    miles = t.str.contains(r"\d,\d{3}\.\d", regex=True)
    t = t.where(~miles, t.str.replace(",", "", regex=False))
    t = t.str.replace(",", ".", regex=False)
    return pd.to_numeric(t.str.extract(r"([-+]?\d+(?:\.\d+)?)", expand=False), errors="coerce")


def _fechas(col):
    """Lee fechas con mes/día y con día/mes. Se queda con la lectura más compacta en el tiempo (un registro dura días,
    no meses); si las dos duran lo mismo, día/mes, como se escribe en México."""
    lecturas = []
    texto = col.astype(str).str.strip()
    iso = texto.str.match(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}").mean() > 0.5     # año primero: siempre año-mes-día
    for dia_primero in ((False,) if iso else (True, False)):
        t = pd.to_datetime(texto, errors="coerce", dayfirst=dia_primero, format="mixed")
        if getattr(t.dt, "tz", None) is not None:      # con zona horaria: a la hora de México, sin zona
            t = t.dt.tz_convert("America/Mexico_City").dt.tz_localize(None)
        ok = t.dropna()
        if len(ok) < 2:
            continue
        retrocesos = int((ok.diff().dt.total_seconds() < 0).sum())
        duracion = (ok.max() - ok.min()).total_seconds()
        lecturas.append((retrocesos, duracion, -int(t.notna().sum()), not dia_primero, t))
    if not lecturas:
        return pd.to_datetime(col, errors="coerce")
    return min(lecturas, key=lambda x: x[:4])[-1]


def _nombre(texto):
    t = str(texto).lower()
    if "temp" in t or "°c" in t or "°f" in t:
        return "temperatura"
    if "hum" in t or "rh" in t or "%" in t:
        return "humedad"
    return None


def _bloque(mascara):
    """Inicio y fin del tramo continuo más largo de renglones con fecha (deja fuera los renglones de informe)."""
    mejor, ini = (0, 0), None
    for i, m in enumerate(list(mascara) + [False]):
        if m and ini is None:
            ini = i
        elif not m and ini is not None:
            if i - ini > mejor[1] - mejor[0]:
                mejor = (ini, i)
            ini = None
    return mejor


def lee_registro(ruta):
    """DataFrame con índice de fecha y hora y una columna por variable (temperatura en °C, humedad en %HR)."""
    AVISOS_LECTURA.clear()
    crudo = _tabla_cruda(ruta)
    cuantas = {c: crudo[c].astype(str).str.contains(PATRON_FECHA, regex=True).sum() for c in crudo.columns}
    col_t = max(cuantas, key=cuantas.get)
    if cuantas[col_t] < 3:
        raise ValueError("No encontré una columna con fechas (por ejemplo 2027-02-15 08:30:00 o 15/02/2027 08:30). "
                         "Revisa que el archivo sea el registro y no un informe en PDF o una imagen.")
    texto_t = crudo[col_t].astype(str)
    sin_hora = ~texto_t.str.contains(r"\d{1,2}:\d{2}", regex=True)
    if sin_hora[texto_t.str.contains(PATRON_FECHA, regex=True)].mean() > 0.5:   # fecha y hora en columnas separadas
        for c in crudo.columns:
            if c != col_t and crudo[c].astype(str).str.contains(PATRON_HORA, regex=True).mean() > 0.5:
                texto_t = texto_t + " " + crudo[c].astype(str)
                AVISOS_LECTURA.append("La fecha y la hora venían en columnas separadas; las uní.")
                break
    t = _fechas(texto_t)
    i0, i1 = _bloque(t.notna().values)
    if i1 - i0 < 10:
        raise ValueError("El archivo tiene menos de 10 renglones con fecha y hora. Si la fecha y la hora están en "
                         "columnas separadas, júntalas en una sola columna en tu hoja de cálculo y vuelve a exportar.")
    datos = pd.Series(False, index=crudo.index)
    datos.iloc[i0:i1] = True
    datos &= t.notna()
    encabezado = crudo.iloc[i0 - 1] if i0 > 0 else pd.Series(dtype=str)
    columnas, raros = {}, []
    for c in crudo.columns:
        if c == col_t:
            continue
        crudos = crudo.loc[datos, c]
        v = _a_numero(crudos)
        if v.notna().mean() < 0.8:
            if crudos.notna().mean() > 0.8 and v.notna().mean() > 0:
                raros.append(str(crudos[v.isna()].iloc[0]))
            continue
        if v.notna().all() and (v.diff().dropna() == 1).all():      # número de renglón (No.): no es una variable
            continue
        texto = str(encabezado.get(c, "")).strip() if len(encabezado) else ""
        texto = "" if texto.lower() in ("nan", "none") else texto
        if crudo[c].astype(str).str.contains(PATRON_HORA, regex=True).mean() > 0.5:
            continue                                                  # la columna de la hora
        nom = _nombre(texto)
        if nom is None and texto and _a_numero(pd.Series([texto])).isna().all():
            nom = texto.lower()
        if "fahrenheit" in texto.lower() or "°f" in texto.lower():
            v = (v - 32) * 5 / 9
            AVISOS_LECTURA.append(f"La columna «{texto}» venía en °F; la convertí a °C.")
        if nom is None:
            nom = "valor"
        if nom in columnas:
            nom = f"{nom}_{len(columnas) + 1}"
        columnas[nom] = v.values
    if not columnas:
        extra = f" Por ejemplo, no pude leer «{raros[0]}» como número." if raros else ""
        raise ValueError("No encontré columnas con números junto a la fecha y hora." + extra)
    tabla = pd.DataFrame(columnas, index=pd.DatetimeIndex(t[datos].values)).sort_index()
    tabla = tabla[~tabla.index.duplicated(keep="last")].dropna(how="all")
    dias = (tabla.index[-1] - tabla.index[0]).total_seconds() / 86400
    if dias > 60:
        AVISOS_LECTURA.append(f"El registro dura {dias:.0f} días. Si tu registro fue de una semana, las fechas se "
                              "leyeron mal (día y mes): avísale al profesor.")
    return tabla


def _campana_sintetica(n):
    """Respaldo mientras las campañas no estén en el repositorio: 7 días cada 60 s, marcados como sintéticos."""
    rng = np.random.default_rng(100 + n)
    t = pd.date_range("2027-02-19 10:00", periods=7 * 1440, freq="60s")
    d = np.arange(t.size) / 1440
    base, amp_dia, comp = [(4.5, 0.4, 1.2), (22.5, 1.8, 0.0), (24.0, 1.0, 0.6)][n - 1]
    x = (base + amp_dia * np.sin(2 * np.pi * (d - 0.35)) + comp * np.sign(np.sin(2 * np.pi * d * 72))
         + 0.15 * d + rng.normal(0, 0.12, t.size))
    x[int(3.2 * 1440):int(3.2 * 1440) + 40] += 4.5                       # una puerta abierta 40 min
    tabla = pd.DataFrame({"temperatura": np.round(x, 1)}, index=t)
    return tabla.drop(tabla.index[int(5.5 * 1440):int(5.5 * 1440) + 150])  # un hueco de 2.5 h


def _sin_acentos(texto):
    import unicodedata
    t = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn" or c == "̃")   # conserva la ñ


def normaliza_fuente(fuente):
    f = _sin_acentos(fuente).replace("campana", "campaña").replace("ñ", "ñ")
    f = " ".join(f.split())
    if f not in FUENTES_REG:
        raise ValueError(f"FUENTE_REG debe ser una de estas, entre comillas: {', '.join(FUENTES_REG)}.")
    return f


def carga_registro(fuente, archivo):
    """Devuelve (tabla, descripción de la fuente, número de la fuente, 1 si es sintético)."""
    import urllib.error
    fuente = normaliza_fuente(fuente)
    numero = FUENTES_REG.index(fuente) + 1
    if fuente.startswith("campaña"):
        n = int(fuente[-1])
        try:
            with urllib.request.urlopen(URL_DATOS + f"campana_{n}.csv", timeout=30) as r:
                open(f"campana_{n}.csv", "wb").write(r.read())
        except Exception as e:  # noqa: BLE001
            no_existe = (isinstance(e, urllib.error.HTTPError) and e.code == 404) or (
                isinstance(e, urllib.error.URLError) and isinstance(getattr(e, "reason", None), FileNotFoundError))
            if not no_existe:
                raise ValueError(f"No pude descargar la campaña {n} ({type(e).__name__}). Revisa tu conexión a "
                                 "internet y vuelve a ejecutar esta celda.") from None
            print(f"⚠ La campaña {n} todavía no está en el repositorio. Uso un registro SINTÉTICO de ejemplo para que "
                  "pruebes el cuaderno; tu entrega debe usar el registro real.")
            return _campana_sintetica(n), f"SINTÉTICO (ejemplo de la campaña {n})", numero, 1
        lugar = ""
        try:
            lista = pd.read_csv(URL_DATOS + "campanas.csv")
            lugar = " · " + str(lista.loc[lista["n"] == n, "lugar"].iloc[0])
        except Exception:  # noqa: BLE001
            pass
        return lee_registro(f"campana_{n}.csv"), f"Campaña RC-5 n.º {n} del grupo{lugar}", numero, 0
    archivo = str(archivo).strip()
    if not archivo:
        raise ValueError("Escribe en ARCHIVO el nombre del archivo que subiste (ícono de carpeta, a la izquierda).")
    if not os.path.exists(archivo):
        raise ValueError(f"No encuentro «{archivo}». Súbelo con el ícono de carpeta del panel izquierdo y copia aquí su "
                         "nombre exacto, con la extensión (.csv o .xlsx). Si Colab se reinició, vuelve a subirlo.")
    nombre = "Govee H5075 en préstamo" if fuente == "govee" else "Datos de su área"
    return lee_registro(archivo), nombre, numero, 0


def elige_columna(tabla, columna):
    cols = list(tabla.columns)
    columna = _sin_acentos(columna)
    if len(cols) == 1:
        if columna and columna != cols[0]:
            print(f"⚠ Tu archivo sólo tiene una variable, «{cols[0]}»; uso ésa aunque escribiste «{columna}».")
        return tabla[cols[0]].dropna(), cols[0]
    if columna not in cols:
        raise ValueError(f"Tu archivo tiene {len(cols)} variables: {', '.join(cols)}. Escribe en COLUMNA la que vas a "
                         "analizar, entre comillas.")
    return tabla[columna].dropna(), columna


def revisa_unidad(unidad, columna):
    u = _sin_acentos(unidad).replace(" ", "").replace("º", "°")
    if columna == "temperatura" and u not in ("°c", "c", "gradosc", "gradoscelsius", "celsius"):
        raise ValueError(f"Tu registro es de temperatura en °C (si venía en °F, el cuaderno ya lo convirtió). Escribe tu "
                         f'plan en °C, con UNIDAD = "°C", y vuelve a ejecutar desde la celda del plan.')
    if columna == "humedad" and "%" not in u:
        raise ValueError('Tu registro es de humedad relativa. Escribe tu plan en %HR, con UNIDAD = "%HR", y vuelve a '
                         "ejecutar desde la celda del plan.")


def recorta(s, inicio_h, fin_h):
    """Quita las horas del principio y del final (cuando el registrador aún no estaba en su lugar)."""
    ini = s.index[0] + pd.Timedelta(hours=float(inicio_h))
    fin = s.index[-1] - pd.Timedelta(hours=float(fin_h))
    if fin <= ini:
        raise ValueError("Con lo que descartas no queda registro: revisa DESCARTA_INICIO_H y DESCARTA_FIN_H.")
    return s[(s.index >= ini) & (s.index <= fin)]


# ------------------------------------------------------------------------------------------- cálculos
def calidad(s):
    dt = s.index.to_series().diff().dt.total_seconds().dropna()
    dt_ef = float(dt.median())
    irregular = bool(dt.quantile(0.9) > 3 * dt_ef)
    if irregular:      # registrador que guarda sólo cuando el valor cambia: se usa el intervalo del percentil 90
        dt_ef = float(dt.quantile(0.9))
    huecos = dt[dt > 1.5 * dt_ef]
    valores = np.unique(np.round(s.values.astype(float), 6))
    pasos = np.diff(valores)
    pasos = pasos[pasos > 1e-9]
    return dict(N_LECT=int(s.size), DT_EF_S=dt_ef, DIAS_REG=(s.index[-1] - s.index[0]).total_seconds() / 86400,
                N_HUECOS=int(huecos.size), HORAS_HUECOS=float((huecos - dt_ef).sum() / 3600),
                HUECOS=[(i - pd.Timedelta(seconds=float(v)), i) for i, v in huecos.items()], IRREGULAR=irregular,
                ESCALON=float(np.round(pasos.min(), 4)) if pasos.size else float("nan"),
                MIN_OBT=float(s.min()), MAX_OBT=float(s.max()), MEDIA_OBT=float(s.mean()))


def rejilla(s, dt_ef):
    """El registro en una rejilla uniforme. Los huecos de hasta 3 intervalos se interpolan; dentro de los huecos más
    largos la rejilla queda vacía (no se inventan datos)."""
    t = pd.date_range(s.index[0], s.index[-1], freq=pd.Timedelta(seconds=dt_ef))
    u = s.reindex(s.index.union(t)).interpolate(method="time", limit_area="inside").reindex(t)
    d = s.index.to_series().diff().dt.total_seconds()
    for fin, largo in d[d > 3 * dt_ef].items():
        ini = fin - pd.Timedelta(seconds=float(largo))
        u[(u.index > ini) & (u.index < fin)] = np.nan
    return u


def filtra(u, ventana_min, dt_ef):
    n = max(1, int(round(ventana_min * 60 / dt_ef)))
    f = u.rolling(n, min_periods=max(1, int(0.8 * n))).mean()
    ruido = float(np.nanstd(np.diff(u.values)) / np.sqrt(2))     # ruido de lectura a lectura
    return f, n, (n - 1) * dt_ef / 2 / 60, ruido, ruido / np.sqrt(n)


def tendencia(u):
    """Recta por mínimos cuadrados a los promedios de los días completos (≥ 80 % de lecturas), en unidad por día.
    Con menos de 3 días completos no se calcula: un ciclo diario incompleto parece tendencia."""
    por_dia = u.groupby(u.index.floor("D"))
    cuenta, media = por_dia.count(), por_dia.mean()
    validos = media[cuenta >= 0.8 * 86400 / ((u.index[1] - u.index[0]).total_seconds())]
    if validos.size < 3:
        return float("nan"), float("nan"), np.array([]), np.array([]), "menos de 3 días completos"
    x = np.array([(d - u.index[0]).total_seconds() / 86400 + 0.5 for d in validos.index])
    m, b = np.polyfit(x, validos.values, 1)
    return float(m), float(b), x, validos.values, f"los promedios de {validos.size} días completos"


def ciclo_dominante(u, dt_ef):
    """Periodo (h) de la componente más fuerte, sin la tendencia. Se busca entre 4 intervalos y un tercio del
    registro; si el máximo cae en un extremo de la búsqueda o no sobresale, no se distingue un ciclo (nan)."""
    v = u.interpolate(limit_direction="both").values.astype(float)
    if v.size < 24 or np.nanstd(v) == 0:
        return float("nan")
    x = np.arange(v.size)
    v = v - np.polyval(np.polyfit(x, v, 1), x)
    w = np.hanning(v.size)
    vw = (v - np.average(v, weights=w)) * w
    n = 8 * v.size
    esp = np.abs(np.fft.rfft(vw, n))
    f = np.fft.rfftfreq(n, d=dt_ef)
    periodo_h = np.full(f.size, np.inf)
    periodo_h[1:] = 1 / f[1:] / 3600
    ok = np.where((periodo_h >= 4 * dt_ef / 3600) & (periodo_h <= v.size * dt_ef / 3600 / 3))[0]
    if ok.size < 3:
        return float("nan")
    k = int(np.argmax(esp[ok]))
    if k in (0, ok.size - 1) or esp[ok][k] < 4 * np.median(esp[ok]):
        return float("nan")
    return float(periodo_h[ok][k])


def alarmas(u, limite, sentido, confirma_min, histeresis, dt_ef):
    """Cruces simples del límite y alarmas con tiempo de confirmación e histéresis (sobre el registro sin filtrar).
    La alarma se enciende cuando el valor lleva CONFIRMA_MIN minutos seguidos del otro lado del límite y se apaga
    cuando regresa más allá de límite − histéresis. Un hueco no es un cruce."""
    sg = 1 if sentido == "arriba" else -1
    y = sg * u.values
    L = sg * limite
    fuera_real = ~np.isnan(y) & (np.nan_to_num(y, nan=-np.inf) > L)
    fuera = pd.Series(np.where(np.isnan(y), np.nan, y > L)).ffill().fillna(0).values.astype(bool)
    cruces = int(fuera[0]) + int(np.sum(fuera[1:] & ~fuera[:-1]))
    confirma_s = confirma_min * 60
    eventos, activa, seguidas, ini = [], False, 0, None
    for i, yi in enumerate(y):
        if np.isnan(yi):
            seguidas = 0
            continue
        if not activa:
            seguidas = seguidas + 1 if yi > L else 0
            if seguidas >= 1 and (seguidas - 1) * dt_ef >= confirma_s - 1e-9:
                activa, ini = True, i
        elif yi < L - histeresis:
            eventos.append((ini, i))
            activa, seguidas = False, 0
    if activa:
        eventos.append((ini, len(y) - 1))
    return cruces, eventos, float(fuera_real.sum() * dt_ef / 3600)


# ------------------------------------------------------------------------------------------- revisiones
def _es_numero(v):
    return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool) and np.isfinite(v)


def _faltan(valores, textos=()):
    faltan, comas = [], []
    for k, v in valores.items():
        if k in textos:
            if not str(v or "").strip():
                faltan.append(k)
        elif isinstance(v, tuple):
            comas.append(k)
        elif not _es_numero(v):
            faltan.append(k)
    mensaje = []
    if faltan:
        mensaje.append("falta " + ", ".join(faltan) + " (números sin comillas; textos entre comillas)")
    if comas:
        mensaje.append("en " + ", ".join(comas) + " usa punto decimal y sin comas de miles: 1200, 0.5")
    return "; ".join(mensaje)


def revisa_plan(VARIABLE, UNIDAD, P_PLAN_S, DT_PLAN_S, EXACT_REQ, EXACT_INSTR, LIMITE, SENTIDO, CONFIRMA_MIN,
                HISTERESIS, VENTANA_MIN):
    valores = dict(locals())
    REGISTRO["Plan"] = False
    falta = _faltan(valores, ("VARIABLE", "UNIDAD", "SENTIDO"))
    if falta:
        raise ValueError("Plan: " + falta + ".")
    if _sin_acentos(SENTIDO) not in ("arriba", "abajo"):
        raise ValueError('Plan: SENTIDO debe ser "arriba" (alarma si se pasa del límite) o "abajo" (si baja del límite).')
    problemas = []
    if min(P_PLAN_S, DT_PLAN_S, EXACT_REQ, EXACT_INSTR, VENTANA_MIN) <= 0:
        problemas.append("el periodo, el intervalo, las exactitudes y la ventana deben ser mayores que 0")
    if min(CONFIRMA_MIN, HISTERESIS) < 0:
        problemas.append("el tiempo de confirmación y la histéresis no pueden ser negativos")
    if not problemas and DT_PLAN_S > P_PLAN_S / 2:
        problemas.append(f"tu intervalo de {DT_PLAN_S:g} s es mayor que P/2 = {P_PLAN_S / 2:g} s: no ves tu fenómeno "
                         "(sesión 2)")
    if problemas:
        raise ValueError("Plan: " + "; ".join(problemas) + ".")
    REGISTRO["Plan"] = True
    if EXACT_INSTR > EXACT_REQ:
        print(f"⚠ El instrumento (± {EXACT_INSTR:g} {UNIDAD}) no alcanza la exactitud que necesitas "
              f"(± {EXACT_REQ:g} {UNIDAD}). Puedes seguir, pero dilo y resuélvelo en tu plan (sesión 4).")
    print(f"✔ Plan completo: {VARIABLE} en {UNIDAD}, cada {DT_PLAN_S:g} s (≤ P/2 = {P_PLAN_S / 2:g} s), alarma si "
          f"va {_sin_acentos(SENTIDO)} de {LIMITE:g} {UNIDAD} durante {CONFIRMA_MIN:g} min, histéresis "
          f"{HISTERESIS:g} {UNIDAD}. La revisión automática sólo comprueba Nyquist: el mínimo del equipo y la memoria "
          "los justificas en tu formato.")


def revisa_predicciones(PRED_MIN, PRED_MAX, PRED_CICLO_H, PRED_TEND, PRED_ALARMAS):
    valores = dict(locals())
    REGISTRO["Predicciones"] = False
    falta = _faltan(valores)
    if falta:
        raise ValueError("Predicciones: " + falta + ".")
    problemas = []
    if PRED_MIN >= PRED_MAX:
        problemas.append("el mínimo debe ser menor que el máximo")
    if PRED_CICLO_H <= 0:
        problemas.append("el ciclo debe ser positivo, en horas")
    if PRED_ALARMAS < 0 or PRED_ALARMAS != int(PRED_ALARMAS):
        problemas.append("las alarmas son un número entero, 0 o más")
    if problemas:
        raise ValueError("Predicciones: " + "; ".join(problemas) + ".")
    REGISTRO["Predicciones"] = True
    print("✔ Predicciones completas. Deben ser las que escribiste con fecha en tu formato, antes del registro.")


def revisa_decision(texto):
    faltan = []
    if _palabras(texto) < 20:
        faltan.append("al menos 20 palabras")
    if not any(t in _sin_acentos(texto) for t in ("correctivo", "preventivo", "condicion", "predictivo")):
        faltan.append("el tipo de mantenimiento que recomiendas (correctivo, preventivo, basado en condición o "
                      "predictivo)")
    REGISTRO["Decisión"] = not faltan
    if faltan:
        raise ValueError("Decisión: falta " + "; ".join(faltan) + ".")
    print("✔ Decisión completa.")


def tabla_plan(plan, obt, unidad):
    """Lo predicho contra lo obtenido. Diferencia absoluta (con unidad) en valores; en % sólo en intervalo y ciclo."""
    U = unidad
    filas = []
    renglones = [(f"Mínimo ({U})", plan["PRED_MIN"], obt["MIN_OBT"], "abs", U),
                 (f"Máximo ({U})", plan["PRED_MAX"], obt["MAX_OBT"], "abs", U),
                 ("Ciclo más visible (h)", plan["PRED_CICLO_H"], obt["CICLO_H"], "pct", ""),
                 (f"Tendencia ({U}/día)", plan["PRED_TEND"], obt["M_OBT"], "abs", f"{U}/día"),
                 ("Alarmas confirmadas", plan["PRED_ALARMAS"], obt["N_ALARMAS"], "abs", ""),
                 ("Intervalo (s)", plan["DT_PLAN_S"], obt["DT_EF_S"], "pct", ""),
                 (f"Resolución: escalón del registro contra exactitud necesaria ({U})", plan["EXACT_REQ"],
                  obt["ESCALON"], "res", ""),
                 (f"Exactitud del instrumento (hoja de datos) contra la necesaria ({U})", plan["EXACT_REQ"],
                  plan["EXACT_INSTR"], "exa", "")]
    for concepto, p, o, tipo, u in renglones:
        if not np.isfinite(o):
            dif = "—"
        elif tipo == "res":
            dif = "distingue lo necesario" if o <= p else "NO distingue lo necesario"
        elif tipo == "exa":
            dif = "alcanza" if o <= p else "NO alcanza"
        elif tipo == "pct":
            pct = round(100 * (o - p) / abs(p)) if abs(p) > 1e-12 else 0
            dif = "0 %" if pct == 0 else f"{pct:+d} %"
        else:
            d = o - p
            dif = (f"{d:+.3g} {u}".strip() if abs(d) > 1e-12 else "0")
        filas.append((concepto, f"{p:.4g}", f"{o:.4g}" if np.isfinite(o) else "no se distingue", dif))
    return pd.DataFrame(filas, columns=["Concepto", "Plan", "Registro", "Diferencia"])


def texto_ciclo(h):
    if not np.isfinite(h):
        return "no se distingue"
    return f"{h:.3g} h ({h * 60:.0f} min)" if h < 1.5 else f"{h:.3g} h"


def eje_dias(s, t0):
    return (s.index - t0).total_seconds() / 86400
'''

# Valores del ejemplo resuelto (versión del profesor y pruebas): un refrigerador de pasta de soldadura con la campaña 1
SOL = {
    "VARIABLE": '"temperatura del aire del refrigerador de pasta de soldadura"', "UNIDAD": '"°C"',
    "P_PLAN_S": "1200", "DT_PLAN_S": "60", "EXACT_REQ": "1.0", "EXACT_INSTR": "0.5",
    "LIMITE": "7.0", "SENTIDO": '"arriba"', "CONFIRMA_MIN": "15", "HISTERESIS": "0.5", "VENTANA_MIN": "60",
    "PRED_MIN": "2.0", "PRED_MAX": "8.0", "PRED_CICLO_H": "24", "PRED_TEND": "0", "PRED_ALARMAS": "1",
    "FUENTE_REG": '"campaña 1"', "ARCHIVO": '""', "COLUMNA": '"temperatura"',
    "DESCARTA_INICIO_H": "0", "DESCARTA_FIN_H": "0",
    "CONCLUSION_B": ('f"El máximo fue {MAX_OBT:.4g} °C contra {PRED_MAX:g} °C que predije y hubo {N_ALARMAS} alarmas '
                     'contra {PRED_ALARMAS:g}. El ciclo más visible no fue el día sino el compresor, porque la puerta '
                     'casi no se abre; mi intervalo de un minuto alcanzó para verlo y el hueco de la descarga no cambió '
                     'la conclusión del registro."'),
    "DECISION": ('"Recomiendo mantenimiento basado en condición: revisar el empaque de la puerta y el compresor sólo '
                 'cuando la alarma confirmada se active, en lugar de una revisión preventiva fija cada mes."'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# Proyecto integrador · Tu registro contra tu plan
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Comprobar tu **plan de adquisición** con un **registro real**: ¿el intervalo alcanzó?, ¿el instrumento distingue lo
que necesitas?, ¿el filtro, la tendencia y la alarma que planeaste dicen algo útil para decidir el mantenimiento?

## En qué consiste este cuaderno
| Paso | Qué haces | Qué escribes (✎) |
|---|---|---|
| 1 · Tu plan | Copias los números de la sección 1 de tu formato | Variable, intervalo, exactitudes, límite, confirmación, histéresis, ventana |
| 2 · Tus predicciones | Escribes lo que esperas **antes de ver el registro** | Mínimo, máximo, ciclo, tendencia y número de alarmas |
| 3 · Tu registro | Cargas tu archivo (Govee o de tu área) o una campaña RC-5 | La fuente, el nombre del archivo y la variable |
| 4 · Calidad | El cuaderno mide duración, intervalo real, huecos y escalón | Nada: lees y comparas |
| 5 · Filtro, tendencia y ciclo | El cuaderno aplica tu ventana, ajusta la recta y busca el ciclo | Nada: lees y comparas |
| 6 · Alarma | El cuaderno cuenta cruces simples y alarmas con tu confirmación e histéresis | Nada: lees y comparas |
| 7 · Plan contra registro | Tabla de lo predicho contra lo obtenido | Tu conclusión y tu decisión |
| Gráficas y CSV | Tres gráficas firmadas y el archivo `PI_<código>.csv` | Nada: las pegas en tu formato |

## Qué entregas
Las tres gráficas, la tabla, tu conclusión, tu decisión y la **huella** van en la sección 2 de tu formato
`F_Proyecto_integrador_DAQ_2027_GGT`. El CSV firmado se sube con el reporte final. Este cuaderno no se califica por
separado: es la herramienta de tu proyecto.

## Reglas
- **Archivo → Guardar una copia en Drive** antes de empezar; trabaja en tu copia.
- Completa sólo lo marcado con ✎. Ninguna celda avanza si falta algo: el mensaje dice qué.
- **Datos de tu área:** sólo con permiso de tu jefe y anonimizados (sin marcas, números de parte, nombres ni ubicación
  exacta). No los subas a repositorios ni a asistentes de IA; bórralos de Colab y de tu Drive al terminar el curso.
- Si usas un asistente de IA, dilo en tu reporte. La conclusión y la decisión llevan **tus** números.
"""),
         cu.guia(),
         cu.herramientas(DATOS_PI)]
    C += cu.identificacion(SESION, nombre, codigo)
    rc5, gov = dp.INSTRUMENTOS["RC-5"], dp.INSTRUMENTOS["Govee H5075"]
    C += [cu.md(f"""
## 1 · Tu plan
Copia los números de la sección 1 de tu formato. Las unidades de `EXACT_REQ`, `EXACT_INSTR`, `LIMITE` e `HISTERESIS`
son las de tu variable.

| Variable | Qué es | Sesión |
|---|---|---|
| `P_PLAN_S` | Periodo del fenómeno más rápido que te interesa, en segundos | 2 |
| `DT_PLAN_S` | Intervalo de registro que planeaste, en segundos | 2 |
| `EXACT_REQ` | Exactitud que necesita tu decisión (±) | 4 |
| `EXACT_INSTR` | Exactitud del instrumento, de su hoja de datos (±). RC-5: {rc5["exactitud"]} °C · Govee H5075: {gov["exactitud"]} °C o {gov["exactitud_hr"]:g} %HR | 4 |
| `LIMITE`, `SENTIDO` | El límite de la alarma y si avisa cuando el valor va `"arriba"` o `"abajo"` de él | 7 |
| `CONFIRMA_MIN` | Minutos seguidos fuera del límite antes de dar la alarma | 7 |
| `HISTERESIS` | Cuánto debe regresar el valor, del otro lado del límite, para apagar la alarma | 7 |
| `VENTANA_MIN` | Ventana del promedio móvil, en minutos | 5 |
"""),
          cu.code("\n".join([
              h("VARIABLE", "✎ qué mides, entre comillas"),
              h("UNIDAD", "✎ su unidad: \"°C\" o \"%HR\""),
              h("P_PLAN_S", "✎ periodo del fenómeno más rápido, en s"),
              h("DT_PLAN_S", "✎ intervalo planeado, en s"),
              h("EXACT_REQ", "✎ exactitud que necesitas, ±"),
              h("EXACT_INSTR", "✎ exactitud del instrumento, ±"),
              h("LIMITE", "✎ límite de la alarma"),
              h("SENTIDO", "✎ \"arriba\" o \"abajo\""),
              h("CONFIRMA_MIN", "✎ tiempo de confirmación, en min"),
              h("HISTERESIS", "✎ histéresis"),
              h("VENTANA_MIN", "✎ ventana del promedio móvil, en min"),
              "",
              "SENTIDO = str(SENTIDO).strip().lower()",
              "revisa_plan(VARIABLE, UNIDAD, P_PLAN_S, DT_PLAN_S, EXACT_REQ, EXACT_INSTR, LIMITE, SENTIDO, CONFIRMA_MIN,",
              "            HISTERESIS, VENTANA_MIN)"])),
          cu.md("""
## 2 · Tus predicciones, antes de ver el registro
Copia las que escribiste en tu formato, con fecha, **antes** de que empezara tu registro (si usas una campaña, antes
de abrir su archivo). Una predicción que se corrige después de ver los datos ya no prueba nada, y no coincidir no
baja tu calificación: lo que cuenta es que expliques por qué. Si no esperas tendencia escribe 0; si esperas que la
variable baje, escríbela negativa.
"""),
          cu.code("\n".join([
              h("PRED_MIN", "✎ mínimo que esperas", vacio="None"),
              h("PRED_MAX", "✎ máximo que esperas", vacio="None"),
              h("PRED_CICLO_H", "✎ periodo del ciclo más visible, en h (un día = 24)", vacio="None"),
              h("PRED_TEND", "✎ tendencia que esperas, por día", vacio="None"),
              h("PRED_ALARMAS", "✎ alarmas que esperas con tu confirmación e histéresis", vacio="None"),
              "",
              "revisa_predicciones(PRED_MIN, PRED_MAX, PRED_CICLO_H, PRED_TEND, PRED_ALARMAS)",
              "PLAN = dict(PRED_MIN=PRED_MIN, PRED_MAX=PRED_MAX, PRED_CICLO_H=PRED_CICLO_H, PRED_TEND=PRED_TEND,",
              "            PRED_ALARMAS=PRED_ALARMAS, DT_PLAN_S=DT_PLAN_S, EXACT_REQ=EXACT_REQ, EXACT_INSTR=EXACT_INSTR)"])),
          cu.md("""
## 3 · Tu registro
`FUENTE_REG` es una de estas cinco:

| `FUENTE_REG` | Qué es | Además escribe |
|---|---|---|
| `"govee"` | Tu registro con el Govee H5075 en préstamo: en la app Govee Home, exporta los datos en CSV | `ARCHIVO` y `COLUMNA` (`"temperatura"` o `"humedad"`) |
| `"area"` | Un registro de tu área, con permiso y anonimizado; una columna con fecha y hora juntas y otra con los valores | `ARCHIVO` |
| `"campaña 1"`, `"campaña 2"`, `"campaña 3"` | Uno de los tres registros RC-5 del grupo; el cuaderno lo descarga solo | Nada más |

Para subir tu archivo: ícono de carpeta (panel izquierdo) → ícono de subir → elige el archivo. Copia su nombre exacto,
con la extensión, en `ARCHIVO`. Si al colocar o al recoger el registrador pasaron unas horas fuera de su lugar (en tu
mano, en el coche), descártalas con `DESCARTA_INICIO_H` y `DESCARTA_FIN_H`, y anótalo en tu bitácora.
"""),
          cu.code("\n".join([
              h("FUENTE_REG", "✎ \"govee\", \"area\", \"campaña 1\", \"campaña 2\" o \"campaña 3\""),
              h("ARCHIVO", "✎ nombre del archivo que subiste (déjalo vacío si usas una campaña)"),
              h("COLUMNA", "✎ \"temperatura\" o \"humedad\" (si tu archivo trae las dos)"),
              h("DESCARTA_INICIO_H", "✎ horas que descartas al inicio (0 si ninguna)", vacio="0"),
              h("DESCARTA_FIN_H", "✎ horas que descartas al final (0 si ninguna)", vacio="0"),
              "",
              "TABLA, FUENTE, FUENTE_N, SINTETICO = carga_registro(FUENTE_REG, ARCHIVO)",
              "for aviso in AVISOS_LECTURA:",
              "    print('⚠', aviso)",
              "print('Variables en el archivo:', ', '.join(TABLA.columns))",
              "SERIE, COLUMNA = elige_columna(TABLA, COLUMNA)",
              "revisa_unidad(UNIDAD, COLUMNA)",
              "SERIE = recorta(SERIE, completa(DESCARTA_INICIO_H, 'DESCARTA_INICIO_H'), completa(DESCARTA_FIN_H, 'DESCARTA_FIN_H'))",
              "T0 = SERIE.index[0]",
              "print(f'Fuente: {FUENTE} · variable: {COLUMNA} · del {SERIE.index[0]:%Y-%m-%d %H:%M} al {SERIE.index[-1]:%Y-%m-%d %H:%M}')"])),
          cu.md("""
## 4 · La calidad del registro
Antes de analizar, se revisa el registro mismo: ¿cuánto duró?, ¿cada cuánto registró de verdad?, ¿se perdieron
datos?, ¿qué tan fino distingue? El **escalón** es la diferencia más chica entre dos valores distintos del registro:
la resolución que de verdad tiene el archivo (sesión 2).

Las gráficas de las secciones 4, 5 y 6 son para revisar. Las que pegas en tu formato salen al final, con tu huella.
"""),
          cu.code("""
globals().update(calidad(SERIE))
print(f"Lecturas: {N_LECT} · duración: {DIAS_REG:.2f} días · intervalo real: {DT_EF_S:g} s (planeado: {DT_PLAN_S:g} s)")
print(f"Huecos (más de 1.5 intervalos sin datos): {N_HUECOS}, que suman {HORAS_HUECOS:.2f} h")
print(f"Escalón observado: {ESCALON:g} {UNIDAD} · exactitud que necesitas: ± {EXACT_REQ:g} {UNIDAD} · "
      f"exactitud del instrumento: ± {EXACT_INSTR:g} {UNIDAD}")
print(f"Mínimo: {MIN_OBT:.4g} · máximo: {MAX_OBT:.4g} · promedio: {MEDIA_OBT:.4g} {UNIDAD}")
if IRREGULAR:
    print(f"⚠ Los intervalos son muy irregulares: tu registrador guarda sólo cuando el valor cambia. Se analiza con una "
          f"rejilla de {DT_EF_S:g} s (el intervalo que cubre 9 de cada 10 lecturas); dilo en tu conclusión.")
if DT_EF_S > P_PLAN_S / 2:
    print(f"⚠ El intervalo real ({DT_EF_S:g} s) es mayor que P/2 = {P_PLAN_S / 2:g} s: este registro no puede mostrar "
          "tu fenómeno más rápido. Dilo en tu conclusión.")
U = rejilla(SERIE, DT_EF_S)

def grafica_registro(res=None):
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(eje_dias(U, T0), U.values, color="#1F5FAD", lw=0.6, label=f"registro ({N_LECT} lecturas)")
    for a, b in HUECOS:
        ax.axvspan((a - T0).total_seconds() / 86400, (b - T0).total_seconds() / 86400, color="#D9822B", alpha=0.35)
    ax.axhline(LIMITE, color="#C62828", ls="--", lw=1, label=f"límite, {LIMITE:g} {UNIDAD}")
    ax.set_xlabel("día del registro"); ax.set_ylabel(f"{COLUMNA} ({UNIDAD})"); ax.grid(alpha=0.3)
    extra = [Patch(color="#D9822B", alpha=0.35, label=f"huecos ({N_HUECOS}, {HORAS_HUECOS:.1f} h)")] if HUECOS else []
    ax.legend(handles=ax.get_legend_handles_labels()[0] + extra, fontsize=8, loc="best")
    titulo(ax, "Mi registro y sus huecos", alumno)
    firma(fig, alumno, res); plt.show()

grafica_registro()
"""),
          cu.md("""
## 5 · Filtro, tendencia y ciclo
El cuaderno aplica **tu** ventana del promedio móvil (sesión 5), ajusta una recta por mínimos cuadrados a los
promedios de cada día completo (sesiones 3 y 5) y busca el **ciclo más visible** del registro: el periodo de la
componente más fuerte una vez quitada la tendencia (sesión 2).
"""),
          cu.code("""
F, N_VENT, RETRASO_MIN, RUIDO, RUIDO_F = filtra(U, VENTANA_MIN, DT_EF_S)
M_OBT, B_OBT, X_DIAS, Y_DIAS, BASE_TEND = tendencia(U)
CICLO_H = ciclo_dominante(U, DT_EF_S)
if DIAS_REG * 24 < 3 * PRED_CICLO_H:
    print(f"⚠ Tu registro dura {DIAS_REG * 24:.0f} h: para distinguir un ciclo de {PRED_CICLO_H:g} h hacen falta al menos "
          f"{3 * PRED_CICLO_H:g} h de registro.")
print(f"Ventana: {VENTANA_MIN:g} min = {N_VENT} lecturas · retraso ({N_VENT} − 1)·{DT_EF_S:g} s / 2 = {RETRASO_MIN:.1f} min")
print(f"Ruido de lectura a lectura: {RUIDO:.3g} {UNIDAD} · después del filtro: {RUIDO_F:.3g} {UNIDAD} (σ/√N)")
if N_VENT == 1:
    print("⚠ Tu ventana es menor que el intervalo real: el promedio móvil no promedia nada.")
sg = 1 if SENTIDO == "arriba" else -1
ultimo = M_OBT * DIAS_REG + B_OBT
if not np.isfinite(M_OBT):
    DIAS_LIMITE = float("nan")
    print(f"Tendencia: no se calcula, tu registro tiene {BASE_TEND}; un ciclo diario incompleto parece tendencia.")
elif sg * (ultimo - LIMITE) >= 0:
    print(f"Tendencia: {M_OBT:.3g} {UNIDAD}/día (recta ajustada a {BASE_TEND}) · predicha: {PRED_TEND:g}")
    DIAS_LIMITE = 0.0
    print("Al final del registro la recta ya está del otro lado del límite.")
elif sg * M_OBT > 0:
    print(f"Tendencia: {M_OBT:.3g} {UNIDAD}/día (recta ajustada a {BASE_TEND}) · predicha: {PRED_TEND:g}")
    DIAS_LIMITE = (LIMITE - ultimo) / M_OBT
    print(f"Días para que la recta llegue al límite, desde el final del registro: {DIAS_LIMITE:.1f}")
    if DIAS_LIMITE > DIAS_REG:
        print(f"⚠ Es más que la duración de tu registro ({DIAS_REG:.1f} días): la recta no lo puede asegurar.")
else:
    print(f"Tendencia: {M_OBT:.3g} {UNIDAD}/día (recta ajustada a {BASE_TEND}) · predicha: {PRED_TEND:g}")
    DIAS_LIMITE = float("nan")
    print("La tendencia no se acerca al límite.")
print(f"Ciclo más visible: {texto_ciclo(CICLO_H)} · predicho: {PRED_CICLO_H:g} h")

def grafica_filtro(res=None):
    fig, ax = plt.subplots(figsize=(10, 3.8))
    d = eje_dias(U, T0)
    ax.plot(d, U.values, color="#CCCCCC", lw=0.5, label="registro")
    ax.plot(d, F.values, color="#1F5FAD", lw=1.4, label=f"promedio móvil de {VENTANA_MIN:g} min")
    if X_DIAS.size:
        ax.plot(X_DIAS, Y_DIAS, "o", color="#0B3C6E", ms=5, label="promedio de cada día")
    if np.isfinite(M_OBT):
        ax.plot([0, DIAS_REG], [B_OBT, M_OBT * DIAS_REG + B_OBT], color="#C62828", lw=2,
                label=f"tendencia: {M_OBT:.3g} {UNIDAD}/día")
    ax.axhline(LIMITE, color="#C62828", ls="--", lw=1)
    ax.set_xlabel("día del registro"); ax.set_ylabel(f"{COLUMNA} ({UNIDAD})"); ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="best")
    titulo(ax, f"Filtro y tendencia · ciclo más visible {texto_ciclo(CICLO_H)}", alumno)
    firma(fig, alumno, res); plt.show()

grafica_filtro()
"""),
          cu.md("""
## 6 · La alarma
Se cuenta de dos maneras sobre el registro sin filtrar (sesiones 7 y 8):
- **Cruces simples:** cada vez que el valor pasa del límite, aunque sea una lectura. Es lo que haría una alarma ingenua.
- **Alarmas confirmadas:** el valor debe quedarse fuera del límite `CONFIRMA_MIN` minutos seguidos para encender la
  alarma, y regresar `HISTERESIS` del otro lado del límite para apagarla. Así se ignoran picos de una lectura y no se
  enciende y apaga mil veces cuando el valor ronda el límite.
"""),
          cu.code("""
N_CRUCES, EVENTOS, HORAS_FUERA = alarmas(U, LIMITE, SENTIDO, CONFIRMA_MIN, HISTERESIS, DT_EF_S)
N_ALARMAS = len(EVENTOS)
print(f"Cruces simples del límite: {N_CRUCES} · alarmas confirmadas: {N_ALARMAS} (predijiste {PRED_ALARMAS:g})")
print(f"Tiempo total del otro lado del límite: {HORAS_FUERA:.2f} h")
for k, (i, j) in enumerate(EVENTOS, 1):
    print(f"  Alarma {k}: del {U.index[i]:%Y-%m-%d %H:%M} al {U.index[j]:%Y-%m-%d %H:%M}")

def grafica_alarma(res=None):
    fig, ax = plt.subplots(figsize=(10, 3.8))
    d = eje_dias(U, T0)
    ax.plot(d, U.values, color="#1F5FAD", lw=0.6, label="registro")
    ax.axhline(LIMITE, color="#C62828", ls="--", lw=1.2, label=f"límite, {LIMITE:g} {UNIDAD}")
    sg = 1 if SENTIDO == "arriba" else -1
    ax.axhline(LIMITE - sg * HISTERESIS, color="#C62828", ls=":", lw=1, label=f"se apaga a {LIMITE - sg * HISTERESIS:g}")
    for i, j in EVENTOS:
        ax.axvspan(d[i], d[j], color="#C62828", alpha=0.25)
    extra = [Patch(color="#C62828", alpha=0.25, label=f"alarmas confirmadas: {N_ALARMAS} (cruces simples: {N_CRUCES})")]
    ax.set_xlabel("día del registro"); ax.set_ylabel(f"{COLUMNA} ({UNIDAD})"); ax.grid(alpha=0.3)
    ax.legend(handles=ax.get_legend_handles_labels()[0] + extra, fontsize=8, loc="best")
    titulo(ax, f"Alarma con {CONFIRMA_MIN:g} min de confirmación", alumno)
    firma(fig, alumno, res); plt.show()

grafica_alarma()
"""),
          cu.md("""
## 7 · Tu plan contra tu registro
La tabla compara lo que predijiste con lo que salió. En los valores la diferencia va con su unidad; en el ciclo y el
intervalo, en porcentaje. Las dos últimas filas separan dos cosas distintas (sesiones 2 y 4):
- **Resolución:** el escalón del registro contra la exactitud que necesitas. Si el escalón es mayor, el archivo no
  distingue lo que tu decisión necesita.
- **Exactitud:** la del instrumento, de su hoja de datos, contra la que necesitas. Un escalón fino no hace exacto a un
  instrumento: un RC-5 muestra décimas, pero garantiza ± 0.5 °C.
"""),
          cu.code("""
OBTENIDO = dict(MIN_OBT=MIN_OBT, MAX_OBT=MAX_OBT, CICLO_H=CICLO_H, M_OBT=M_OBT, N_ALARMAS=N_ALARMAS,
                DT_EF_S=DT_EF_S, ESCALON=ESCALON)
TABLA_PLAN = tabla_plan(PLAN, OBTENIDO, UNIDAD)
TABLA_PLAN
"""),
          cu.md("""
### Tu conclusión
¿En qué acertó tu plan y en qué no, y por qué? Usa al menos tu máximo obtenido y tus alarmas confirmadas, comparados
con lo que predijiste. Al menos 40 palabras.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión', CONCLUSION_B, {'el máximo obtenido': MAX_OBT,\n"
                  "             'las alarmas confirmadas': N_ALARMAS}, minimo=40)"),
          cu.md("""
### Tu decisión
Con este registro, ¿qué mantenimiento recomiendas para tu variable: correctivo, preventivo, basado en condición o
predictivo? ¿Qué harías y cuándo? Al menos 20 palabras.
"""),
          cu.code(h("DECISION") + "\n\nrevisa_decision(DECISION)"),
          cu.md("""
## Tus gráficas y tu CSV
Las tres gráficas salen ahora con tu **huella**: cópialas (clic derecho → Copiar imagen) en la sección 2 de tu
formato. La celda descarga `PI_<código>.csv`, que subes con tu reporte final.
"""),
          cu.code("""
RESULTADOS = {"n_lect": N_LECT, "dias_reg": DIAS_REG, "dt_ef_s": DT_EF_S, "n_huecos": N_HUECOS,
              "horas_huecos": HORAS_HUECOS, "escalon": ESCALON, "min_obt": MIN_OBT, "max_obt": MAX_OBT,
              "media_obt": MEDIA_OBT, "ventana_min": VENTANA_MIN, "retraso_min": RETRASO_MIN, "m_obt": M_OBT,
              "ciclo_h": CICLO_H, "dias_limite": DIAS_LIMITE, "n_cruces": N_CRUCES, "n_alarmas": N_ALARMAS,
              "horas_fuera": HORAS_FUERA, "pred_min": PRED_MIN, "pred_max": PRED_MAX, "pred_ciclo_h": PRED_CICLO_H,
              "pred_tend": PRED_TEND, "pred_alarmas": PRED_ALARMAS, "dt_plan_s": DT_PLAN_S, "p_plan_s": P_PLAN_S,
              "exact_req": EXACT_REQ, "exact_instr": EXACT_INSTR, "limite": LIMITE, "confirma_min": CONFIRMA_MIN,
              "histeresis": HISTERESIS, "fuente_n": FUENTE_N, "sintetico": SINTETICO}
grafica_registro(RESULTADOS)
grafica_filtro(RESULTADOS)
grafica_alarma(RESULTADOS)
ruta = f"PI_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {c: list(TABLA_PLAN[c]) for c in TABLA_PLAN.columns},
             extra={"fuente": FUENTE, "variable": f"{COLUMNA} ({UNIDAD})",
                    "periodo": f"{SERIE.index[0]:%Y-%m-%d %H:%M} a {SERIE.index[-1]:%Y-%m-%d %H:%M}",
                    "plan": VARIABLE, "sentido": SENTIDO})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
""")]
    C += cu.cierre()
    if prof:
        C += [cu.md("""
---
# Sólo profesor · Verificación de los CSV del proyecto
Sube los `PI_<código>.csv` entregados (ícono de carpeta) y ejecuta. Para cada uno dice si la huella es válida (el CSV
no se editó después de generarlo) y si el registro es sintético; la tabla lista los números para que los compares con
los que el alumno pegó en su formato. La marca de sintético va dentro de la huella: si alguien cambia la fuente a
mano, el número no cambia o la huella deja de ser válida.
"""),
              cu.code('''
import glob
filas = []
for ruta in sorted(glob.glob("PI_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    valida = verificar_csv(ruta)
    sintetico = res.get("sintetico", 0) == 1 or "SINTÉTICO" in str(meta.get("fuente", ""))
    filas.append({"archivo": ruta, "nombre": meta["nombre"], "codigo": meta["codigo"],
                  "huella": "válida" if valida else "NO VÁLIDA", "fuente": meta.get("fuente"),
                  "variable": meta.get("variable"), "dias": round(res.get("dias_reg", 0), 2),
                  "max": res.get("max_obt"), "pred_max": res.get("pred_max"),
                  "alarmas": res.get("n_alarmas"), "pred_alarmas": res.get("pred_alarmas"),
                  "revisar": "registro sintético" if sintetico else ""})
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if valida else 'NO VÁLIDA'} · fuente {meta.get('fuente')}"
          + (" · revisar: registro sintético" if sintetico else ""))
pd.DataFrame(filas)
''')]
    return C


if __name__ == "__main__":
    cu.guardar(celdas(), ALUMNO)
    cu.guardar(celdas(prof=True), PROF)
    print("listo:", ALUMNO, PROF, sep="\n  ")
    if len(sys.argv) == 3 and sys.argv[1] == "--prueba":
        cu.guardar(celdas(r="numero", nombre="Alumno De Prueba", codigo="217654321"),
                   os.path.join(sys.argv[2], f"{SESION}_numeros.ipynb"))
        ruta = cu.guardar(celdas(r=True, nombre="Alumno De Prueba", codigo="217654321"),
                          os.path.join(sys.argv[2], f"{SESION}_resuelto.ipynb"))
        print("  prueba:", ruta)
