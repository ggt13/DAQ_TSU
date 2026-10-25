"""Sesión 5 · Ruido, filtrado y tendencias. Genera:

    S5_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S5_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S5_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s5.py            -> los tres archivos
      python gen_s5.py --prueba D -> además, una versión resuelta en D para ejecutarla

Parte A: registro sintético de 14 días de un equipo de planta que se calienta poco a poco (tendencia + ciclo diario +
ruido + picos), con parámetros por código. Parte B: 60 días de temperatura horaria real de Guadalajara (Open-Meteo,
ERA5, CC BY 4.0), con ventana de fechas por código. Si Open-Meteo no responde, se usa la copia del repositorio
(datos/open_meteo_gdl_2025.csv, la arma prepara_respaldo.py) y, si tampoco existe, datos sintéticos marcados.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S5"
CARPETA = "sesion_05_ruido_y_tendencias"
ALUMNO = os.path.join(AQUI, "S5_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S5_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S5_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S5_AC_CLASE_Colab_ALUMNO.ipynb"
URL_RESPALDO = "https://raw.githubusercontent.com/ggt13/DAQ_TSU/main/" + CARPETA + "/datos/open_meteo_gdl_2025.csv"

DATOS_S5 = f'URL_RESPALDO = "{URL_RESPALDO}"\n' + r'''
import pandas as pd

EQUIPOS = [  # lugar, causa del calentamiento, temperatura de arranque típica (°C), límite del promedio diario (°C)
    ("Gabinete de un variador de frecuencia", "el filtro de entrada de aire se va tapando", 33, 45),
    ("Carcasa del motor de una bomba de agua helada", "la grasa del rodamiento se degrada", 52, 65),
    ("Tablero eléctrico de una línea SMT", "una conexión se afloja y calienta", 35, 48),
    ("Aceite de una prensa hidráulica", "el enfriador pierde eficiencia", 45, 58),
    ("Fuente de poder de un probador funcional", "el ventilador pierde velocidad", 38, 50),
]
DIAS_A = 14                  # duración del registro de la parte A
DIAS_B = 60                  # duración del registro de la parte B
DIAS_SEM = 53                # días entre el centro de la primera semana y el de la última, en 60 días
LIMITE_B = 26.0              # límite del promedio diario del aire de entrada a los gabinetes (parte B), °C
HORIZONTE_B = 30             # la recta de la parte B no se extrapola más allá de la mitad del registro, días
URL_CLIMA = ("https://archive-api.open-meteo.com/v1/archive?latitude=20.67&longitude=-103.35&models=era5"
             "&start_date={}&end_date={}&hourly=temperature_2m&timezone=America%2FMexico_City")


def datos_s5(alumno):
    """El registro personal de la parte A: 14 días de un equipo que se calienta, con ruido y picos."""
    lugar, causa, base, limite = asignar(alumno, EQUIPOS)
    t0 = base + parametro(alumno, "T0", -1.5, 1.5, 2)
    m = parametro(alumno, "pendiente", 0.15, 0.45, 3)
    amp = parametro(alumno, "ciclo", 0.8, 2.5, 2)
    sigma = parametro(alumno, "sigma", 0.15, 0.45, 2)
    dt = asignar(alumno, [5, 10, 15], salto=1)
    n_vent = asignar(alumno, [6, 9, 12, 16], salto=2)
    n_picos = asignar(alumno, [3, 4, 5, 6], salto=3)
    por_dia = 1440 // dt
    t_d = np.arange(0, DIAS_A * 1440, dt) / 1440
    limpia = t0 + m * t_d + amp * np.sin(2 * np.pi * (t_d - 0.375))       # máximo hacia las 15 h
    sin_picos = np.round(limpia + alumno.rng("ruido").normal(0, sigma, t_d.size), 1)
    con_picos = sin_picos.copy()
    idx = alumno.rng("picos").choice(np.arange(por_dia, t_d.size - por_dia), n_picos, replace=False)
    con_picos[idx] = np.round(con_picos[idx] + alumno.rng("magnitud").uniform(10, 18, n_picos), 1)
    return dict(LUGAR=lugar, CAUSA=causa, LIMITE=limite, DT_MIN=dt, N_VENT=n_vent, SIGMA=sigma, N_PICOS=n_picos,
                POR_DIA=por_dia, T_D=t_d, T_REG=con_picos, T_SIN_PICOS=sin_picos, T_LIMPIA=limpia,
                T_DIA1=round(float(np.mean(con_picos[:por_dia])), 2),
                T_DIA_ULT=round(float(np.mean(con_picos[-por_dia:])), 2), DIAS_ENTRE=DIAS_A - 1)


def clave_s5(alumno):
    """Resultados esperados de la parte A."""
    d = datos_s5(alumno)
    m = (d["T_DIA_ULT"] - d["T_DIA1"]) / d["DIAS_ENTRE"]
    return {"m_tend": m, "dias_limite": (d["LIMITE"] - d["T_DIA_ULT"]) / m,
            "sigma_f": d["SIGMA"] / np.sqrt(d["N_VENT"]), "retraso_min": (d["N_VENT"] - 1) * d["DT_MIN"] / 2}


def media_movil(x, n):
    """Promedio de las últimas n lecturas (filtro causal, como el que corre en un registrador en tiempo real)."""
    return pd.Series(x).rolling(int(n)).mean().to_numpy()


def mediana_movil(x, n):
    """Mediana de las últimas n lecturas."""
    return pd.Series(x).rolling(int(n)).median().to_numpy()


def efecto_picos(d):
    """El pico de mayor tamaño y cuánto mueve a cada filtro mientras está dentro de la ventana (°C)."""
    n = d["N_VENT"]
    i = int(np.argmax(d["T_REG"] - d["T_SIN_PICOS"]))
    z = slice(i, i + n)
    dm = np.nanmax(np.abs(media_movil(d["T_REG"], n) - media_movil(d["T_SIN_PICOS"], n))[z])
    dk = np.nanmax(np.abs(mediana_movil(d["T_REG"], n) - mediana_movil(d["T_SIN_PICOS"], n))[z])
    return float(dm), float(dk), i


def ruido_medido(d):
    """Desviación estándar del ruido que queda después del promedio móvil (sin picos): se compara con sigma_f."""
    n = d["N_VENT"]
    return float(np.nanstd(media_movil(d["T_SIN_PICOS"], n) - media_movil(d["T_LIMPIA"], n), ddof=1))


def _clima_open_meteo(inicio, fin):
    import json, urllib.request
    with urllib.request.urlopen(URL_CLIMA.format(inicio, fin), timeout=30) as resp:
        return np.array(json.load(resp)["hourly"]["temperature_2m"], dtype=float)


def _clima_copia(inicio, fin):
    tabla = pd.read_csv(URL_RESPALDO, parse_dates=["time"])
    k = (tabla["time"] >= pd.Timestamp(inicio)) & (tabla["time"] < pd.Timestamp(fin) + pd.Timedelta(days=1))
    return tabla.loc[k, "temperature_2m"].to_numpy(dtype=float)


def carga_clima(alumno, primero_copia=False):
    """60 días de temperatura horaria de Guadalajara; la ventana de fechas depende del código.

    Orden: Open-Meteo, copia del repositorio (los mismos datos) y, si ninguna responde, datos sintéticos marcados.
    El profesor usa primero la copia para no descargar de nuevo cada alumno.
    """
    import datetime as dt
    inicio = dt.date(2025, 1, 13) + dt.timedelta(days=int(alumno.codigo) % 60)
    fin = inicio + dt.timedelta(days=DIAS_B - 1)
    fuentes = [("Open-Meteo (ERA5), Guadalajara", _clima_open_meteo),
               ("Open-Meteo (ERA5), Guadalajara · copia del repositorio", _clima_copia)]
    if primero_copia:
        fuentes.reverse()
    avisos = []
    for nombre, lee in fuentes:
        try:
            T = lee(inicio, fin)
            if T.size != DIAS_B * 24 or np.isnan(T).any():
                raise ValueError("faltan horas en tus fechas")
            if avisos and not primero_copia:
                print("⚠ Open-Meteo no respondió; se usa la copia del repositorio, que tiene los mismos datos.")
            return T, nombre, inicio, fin
        except Exception as e:
            avisos.append(f"{nombre}: {type(e).__name__} {e}")
    for a in avisos:
        print("⚠ No se pudo leer", a)
    print("⚠ Se usan datos SINTÉTICOS. Vuelve a ejecutar esta celda con internet antes de entregar.")
    g = alumno.rng("clima")
    h = np.arange(DIAS_B * 24)
    clima = np.zeros(h.size)
    for i in range(1, h.size):                       # frentes y días nublados: variación lenta de varios días
        clima[i] = 0.995 * clima[i - 1] + g.normal(0, 0.12)
    T = 17 + 0.09 * h / 24 + 7 * np.sin(2 * np.pi * (h - 9) / 24) + clima + g.normal(0, 0.4, h.size)
    return np.round(T, 1), "SINTÉTICOS (sin conexión)", inicio, fin


def tendencia_clima(T):
    """Promedios diarios, promedios de la primera y la última semana, recta de los promedios diarios,
    dispersión de los promedios alrededor de la recta (el clima de cada semana) y días con promedio sobre el límite."""
    diaria = T.reshape(DIAS_B, 24).mean(axis=1)
    dias = np.arange(DIAS_B) + 0.5
    m, b = np.polyfit(dias, diaria, 1)
    return dict(DIAS=dias, T_DIARIA=diaria, T_SEM1=round(float(diaria[:7].mean()), 2),
                T_SEM2=round(float(diaria[-7:].mean()), 2), M_OBT=float(m), B_OBT=float(b),
                S_CLIMA=float(np.std(diaria - (m * dias + b), ddof=2)),
                CICLO_B=float(np.mean(T.reshape(DIAS_B, 24).max(axis=1) - T.reshape(DIAS_B, 24).min(axis=1)) / 2),
                DIAS_SOBRE=int(np.sum(diaria > LIMITE_B)))


def dias_al_limite(m, b, limite=LIMITE_B):
    """Días, desde el final del registro, para que la recta llegue al límite.

    0: la recta ya lo rebasa. −1: la tendencia no sube o tardaría más de HORIZONTE_B días; más allá la recta no
    sirve, porque la temperatura de la estación es un ciclo anual y no una línea recta.
    """
    if m <= 0:
        return -1.0
    dias = (limite - (m * DIAS_B + b)) / m
    if dias <= 0:
        return 0.0
    return float(dias) if dias <= HORIZONTE_B else -1.0


def prepara_ventana(v):
    """Convierte la ventana que escribió el alumno en número de horas, o dice qué falta."""
    if v is None:
        raise ValueError("Escribe la ventana del filtro, en horas, en VENTANA_H.")
    try:
        v = float(v)
    except (TypeError, ValueError):
        raise ValueError("VENTANA_H debe ser un número de horas, sin comillas (por ejemplo 24).") from None
    if v < 1 or v != int(v):
        raise ValueError("VENTANA_H debe ser un número entero de horas, al menos 1.")
    return v


def revisa_ventana(v):
    """La ventana del filtro de la parte B: debe abarcar días completos y no pasar de una semana."""
    faltan = []
    if int(v) % 24 != 0:
        faltan.append(f"con {v:g} h el ciclo día–noche sigue en la señal filtrada (mira la gráfica): la ventana debe "
                      "abarcar días completos")
    if v > 168:
        faltan.append(f"con {v:g} h el filtro se retrasa {(v - 1) / 48:.1f} días: no pases de una semana (168 h)")
    REGISTRO["Ventana del filtro"] = not faltan
    if faltan:
        raise ValueError("Ventana del filtro: " + "; ".join(faltan) + ".")
    print(f"✔ Ventana de {v:g} h: abarca {int(v) // 24} día(s) completo(s).")
'''

SOL = {
    "m_tend": "(T_DIA_ULT - T_DIA1) / DIAS_ENTRE",
    "SUST_1": 'f"({T_DIA_ULT:.2f} − {T_DIA1:.2f}) °C / {DIAS_ENTRE} días = {m_tend:.4g} °C/día"',
    "PRED_1": '"el equipo se calienta esa cantidad cada día aunque el ciclo de día y noche lo esconda en la gráfica"',
    "dias_limite": "(LIMITE - T_DIA_ULT) / m_tend",
    "SUST_2": 'f"({LIMITE} − {T_DIA_ULT:.2f}) °C / {m_tend:.4g} °C/día = {dias_limite:.4g} días"',
    "PRED_2": '"si nada cambia el promedio diario llega al límite en ese tiempo y la intervención debe programarse antes"',
    "sigma_f": "SIGMA / np.sqrt(N_VENT)",
    "SUST_3": 'f"{SIGMA} °C / √{N_VENT} = {sigma_f:.4g} °C"',
    "PRED_3": '"la línea filtrada se verá mucho más tranquila que el registro crudo porque el ruido aleatorio se promedia"',
    "retraso_min": "(N_VENT - 1) * DT_MIN / 2",
    "SUST_4": 'f"({N_VENT} − 1) × {DT_MIN} min / 2 = {retraso_min:.4g} min"',
    "PRED_4": '"la señal filtrada llegará tarde a cualquier cambio rápido, así que una alarma sobre ella avisa con retraso"',
    "CIERRE": ('f"El pico de mayor tamaño movió el promedio móvil {d_media:.3g} °C y la mediana móvil sólo {d_mediana:.3g} °C; '
               'para la alarma de mi equipo usaría la mediana porque ignora las lecturas falsas aisladas"'),
    "VENTANA_H": "24",
    "m_pred": "(T_SEM2 - T_SEM1) / DIAS_SEM",
    "CONCLUSION_B": ('f"Con dos semanas predije {m_pred:.3g} °C/día y la recta de los 60 promedios diarios dio '
                     '{m_obt:.3g} °C/día; la diferencia viene del clima de cada semana, por eso la recta usa todos los días"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# S5 · Ruido, filtrado y tendencias · ¿Se está calentando o es puro ruido?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Separar en un registro real lo que es **tendencia** (el proceso cambia), **ciclo** (se repite cada día) y **ruido**
(no se repite), con **filtros móviles** (promedio y mediana), y usar la tendencia para decidir **cuándo intervenir**
antes de llegar a un límite: mantenimiento **preventivo** basado en datos.

## La situación
Un registrador lleva 14 días en un equipo de la planta que se calienta poco a poco: un filtro que se tapa, una grasa
que se degrada, una conexión que se afloja. En la gráfica cruda casi no se nota: el ciclo de día y noche, el ruido del
sensor y algunas lecturas falsas lo esconden. Cada alumno tiene un equipo distinto, con su propia tendencia, ruido y
picos. En la práctica haces lo mismo con 60 días de temperatura horaria de Guadalajara (reanálisis ERA5).

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero) sobre **tu** equipo: tendencia, días al límite, cuánto baja el ruido con el filtro y cuánto se retrasa. En cada uno escribes tu resultado, la sustitución con tus números y su unidad, y lo que predice | Cuántos días faltan para tu intervención preventiva y la elección del filtro |
| **B · Práctica** | 80 min | Filtras 60 días de temperatura de Guadalajara, eliges la ventana que elimina el ciclo diario, predices la tendencia con dos semanas y la comparas con la recta de todos los días | Gráficas firmadas, tu conclusión y el archivo `S5_<código>.csv` |
| **Hoja de resultados** | en la práctica | Importas el CSV en tu hoja de cálculo de Google y contestas las preguntas | El reporte que entregas |

## Qué entregas y cómo se califica
1. **Este cuaderno**, al terminar la sesión, con todo ejecutado. ★ 3 pts · ejercicios 2, 3 y 4, 2 pts cada uno ·
   cierre 1 pt. Se califica que el resultado sea correcto para **tus** datos y que la sustitución y la predicción
   sean tuyas.
2. **La hoja de resultados** con el reporte, en 7 días naturales.

## Reglas
- **Archivo → Guardar una copia en Drive** antes de empezar; trabaja en tu copia.
- Completa sólo lo marcado con ✎. Ninguna celda avanza si falta algo: el mensaje dice qué.
- La revisión automática dice si el ejercicio está **completo**, no si está **bien**; eso lo califica el profesor.
- Si usas un asistente de IA, dilo en tu reporte. Las sustituciones y las respuestas llevan **tus** números.
"""),
         cu.guia(),
         cu.herramientas(DATOS_S5)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** equipo y su registro de 14 días. El cuaderno ya calculó los promedios del primer y
del último día: el promedio de un día completo **cancela el ciclo día–noche** (lo que sube de día se compensa con lo
que baja de noche) y deja ver la tendencia. Tu `LIMITE` es un límite del **promedio diario**: el máximo de cada
tarde lo toca unos días antes.

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
m_tend = 0.300
SUST_1 = "(44.10 − 40.20) °C / 13 días = 0.300 °C/día"
PRED_1 = "el compresor se calienta tres décimas de grado cada día aunque en la gráfica cruda no se note"
```
Para escribir **°** copia este símbolo: ° (o en Windows, Alt + 0176). También se acepta «C/día» o «grados».
"""),
          cu.code("""
globals().update(datos_s5(alumno))
print(f"Tu equipo · {LUGAR}: {CAUSA}")
print(f"  Registro de {DIAS_A} días, una lectura cada DT_MIN = {DT_MIN} min ({POR_DIA} lecturas por día, {T_REG.size} en total)")
print(f"  Límite del promedio diario: LIMITE = {LIMITE} °C")
print(f"  Promedio del primer día: T_DIA1 = {T_DIA1:.2f} °C · del último día: T_DIA_ULT = {T_DIA_ULT:.2f} °C · "
      f"días entre ellos: DIAS_ENTRE = {DIAS_ENTRE}")
print(f"  Ruido del sensor (medido en banco con el equipo apagado): SIGMA = {SIGMA} °C")
print(f"  Filtro que trae el registrador: ventana de N_VENT = {N_VENT} lecturas")
fig, ax = plt.subplots()
ax.plot(T_D, T_REG, color="#9DB7D5", lw=0.6)
ax.axhline(LIMITE, color="#C62828", ls="--", lw=1, label=f"límite del promedio diario, {LIMITE} °C")
ax.set_xlabel("día"); ax.set_ylabel("T (°C)"); ax.legend(loc="upper left", fontsize=8)
titulo(ax, "Tu registro crudo", alumno)
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### ★ Ejercicio 1 · ¿Cuánto se calienta por día? (3 pts)
**Para qué sirve:** la **tendencia** es lo que anuncia la falla; el ciclo y el ruido no. Sin ella no hay mantenimiento
preventivo basado en datos.

Con los promedios del primer y del último día: **m = (T̄_último − T̄_primero) / días entre ellos**. Calcula `m_tend`
en °C/día.
"""),
          cu.ejercicio(h, 1, "m_tend", [("tu promedio del primer día", "T_DIA1"),
                                        ("tu promedio del último día", "T_DIA_ULT"),
                                        ("los días entre ellos", "DIAS_ENTRE")],
                      ["°C/día", "C/día", "C/dia", "grados/día", "grados por día"]),
          cu.md("""
### Ejercicio 2 · ¿Cuándo llega al límite? (2 pts)
**Para qué sirve:** es la fecha que se lleva a la junta de mantenimiento: la intervención se programa **antes**.

Si la tendencia sigue igual, ¿cuántos días faltan, contados desde el **último día** del registro, para que el
**promedio diario** llegue a tu `LIMITE`? Usa tu `m_tend`. Resultado en días.
"""),
          cu.ejercicio(h, 2, "dias_limite", [("tu límite", "LIMITE"), ("tu promedio del último día", "T_DIA_ULT"),
                                             ("tu tendencia", "m_tend")], ["día", "dia"]),
          cu.md("""
### Ejercicio 3 · ¿Cuánto ruido quita el filtro? (2 pts)
**Para qué sirve:** decide si el filtro del registrador basta para ver cambios pequeños.

Al promediar `N_VENT` lecturas con ruido **aleatorio** e independiente, la desviación estándar del ruido se
**divide entre la raíz cuadrada** del número de lecturas promediadas. Calcula la desviación que queda, `sigma_f`,
en °C.
"""),
          cu.ejercicio(h, 3, "sigma_f", [("tu ruido", "SIGMA"), ("tu ventana", "N_VENT")], ["°C", " C", "grados"]),
          cu.md("""
### Ejercicio 4 · ¿Cuánto se retrasa el filtro? (2 pts)
**Para qué sirve:** un filtro que sólo usa lecturas pasadas (como el de un registrador en tiempo real) responde tarde;
una alarma sobre la señal filtrada avisa con ese retraso.

El promedio de las últimas N lecturas representa el instante que está **a la mitad** de la ventana. Ese instante
queda (N − 1)/2 intervalos atrás de la lectura más reciente. Calcula el retraso, `retraso_min`, en minutos.
"""),
          cu.ejercicio(h, 4, "retraso_min", [("tu ventana", "N_VENT"), ("tu intervalo", "DT_MIN")], ["min"]),
          cu.md("""
### Promedio móvil contra mediana móvil
La gráfica aplica a tu registro los dos filtros con tu ventana de `N_VENT` lecturas. Abajo, un acercamiento al
**pico de mayor tamaño**: una lectura falsa, como las que deja un cable flojo o una interferencia. El promedio la
reparte entre las lecturas vecinas; la mediana casi no la nota, porque aguanta hasta (N − 1)/2 lecturas falsas dentro
de la ventana. Debajo de la gráfica, el cuaderno compara tu predicción del ejercicio 3 con el ruido que de verdad quedó.
"""),
          cu.code("""
f_media, f_mediana = media_movil(T_REG, N_VENT), mediana_movil(T_REG, N_VENT)
d_media, d_mediana, i = efecto_picos(datos_s5(alumno))
sigma_medido = ruido_medido(datos_s5(alumno))
z = slice(max(0, i - POR_DIA // 4), min(T_REG.size, i + POR_DIA // 4))
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.4))
a1.plot(T_D, T_REG, color="#BBBBBB", lw=0.6, label="crudo")
a1.plot(T_D, f_media, color="#1F5FAD", lw=1.2, label=f"promedio de {N_VENT} lecturas")
a1.plot(T_D, f_mediana, color="#D9822B", lw=1.2, label=f"mediana de {N_VENT} lecturas")
a1.axhline(LIMITE, color="#C62828", ls="--", lw=1)
a1.set_ylabel("T (°C)"); a1.legend(fontsize=8, ncol=3); titulo(a1, "Tu registro filtrado", alumno)
a2.plot(T_D[z] * 24, T_REG[z], "o", color="#BBBBBB", ms=3)
a2.plot(T_D[z] * 24, f_media[z], color="#1F5FAD", lw=1.5); a2.plot(T_D[z] * 24, f_mediana[z], color="#D9822B", lw=1.5)
bajo, alto = np.nanmin(T_SIN_PICOS[z]) - 0.5, np.nanmax(f_media[z]) + 1.0
a2.set_ylim(bajo, alto)
a2.annotate(f"lectura falsa: {T_REG[i]:.1f} °C (fuera de escala)", xy=(T_D[i] * 24, alto), xytext=(T_D[i] * 24, alto - 0.4),
            ha="center", fontsize=8, arrowprops=dict(arrowstyle="->", color="#666"))
a2.set_xlabel("hora desde el inicio del registro"); a2.set_ylabel("T (°C)")
a2.set_title("Acercamiento al pico de mayor tamaño")
firma(fig, alumno); plt.tight_layout(rect=(0, 0.05, 1, 1)); plt.show()
print(f"Tu registro tiene {N_PICOS} lecturas falsas. Mientras el pico de mayor tamaño está en la ventana, movió el "
      f"promedio móvil {d_media:.3g} °C y la mediana móvil {d_mediana:.3g} °C.")
print(f"Lecturas sobre la línea roja: crudo {int(np.sum(T_REG > LIMITE))} · promedio móvil "
      f"{int(np.nansum(f_media > LIMITE))} · mediana móvil {int(np.nansum(f_mediana > LIMITE))}. "
      "Una alarma sobre el dato crudo daría falsas alarmas.")
print(f"Ruido después del promedio móvil: predicho (ejercicio 3) {sigma_f:.3g} °C · medido {sigma_medido:.3g} °C")
print(f"Relación señal-ruido de un día de calentamiento ({m_tend:.3g} °C): con el dato crudo {m_tend / SIGMA:.3g}, "
      f"con el filtrado {m_tend / sigma_f:.3g}")
"""),
          cu.md("""
### Cierre (1 pt)
¿Cuánto movió el pico de mayor tamaño a cada filtro (números impresos arriba) y cuál usarías para la alarma de tu equipo?
¿Por qué? Al menos 20 palabras, con los dos números.
"""),
          cu.code(h("CIERRE") + "\n\nrevisa_texto('Cierre', CIERRE, {'lo que el pico movió al promedio': d_media,\n"
                  "             'lo que el pico movió a la mediana': d_mediana})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** con datos reales, elegir la ventana que elimina el ciclo diario y medir la tendencia de 60 días.

Imagina que el aire de la nave entra a los gabinetes eléctricos: si el **promedio diario** pasa de 26 °C, los
equipos trabajan calientes (cada tarde la temperatura horaria pasa de 26 °C; eso no cuenta). Los datos son 60 días de
temperatura horaria de Guadalajara del **reanálisis ERA5** (Copernicus/ECMWF: un modelo del clima ajustado con
observaciones, en celdas de unos 25 km), servidos por [Open-Meteo](https://open-meteo.com/) con licencia CC BY 4.0;
las fechas dependen de tu código. Entre enero y mayo la temperatura sube con la estación, pero cada semana el clima la
mueve para arriba o para abajo.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos | 10 | Descargas los 60 días y miras el ciclo día–noche |
| B2 · Ventana | 20 | Pruebas ventanas del promedio móvil y eliges la que elimina el ciclo |
| B3 · Predicción | 10 | Calculas la tendencia con dos semanas, como en el ★ |
| B4 · Tendencia | 15 | El cuaderno ajusta la recta a los 60 promedios diarios; comparas |
| B5 · Conclusión | 15 | Comparas predicho contra obtenido y decides, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
T_hora, FUENTE, inicio, fin = carga_clima(alumno)
HORAS = T_hora.size
print(f"B1 · Del {inicio} al {fin} · {HORAS} lecturas horarias · fuente: {FUENTE}")
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(np.arange(HORAS) / 24, T_hora, color="#9DB7D5", lw=0.6)
ax.set_xlabel("día"); ax.set_ylabel("T (°C)"); ax.set_xticks(range(0, 61, 5)); ax.grid(alpha=0.3)
titulo(ax, "Temperatura horaria de Guadalajara", alumno)
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### B2 · La ventana del promedio móvil
Escribe en `VENTANA_H` una ventana en horas y ejecuta. Prueba primero **6** y **18**: el ciclo día–noche sigue
ahí, más chico, y la celda **termina en rojo a propósito**: lee el mensaje. Luego prueba **24**. Deja la ventana que
elimina el ciclo; la celda revisa que abarque días completos.
"""),
          cu.code(h("VENTANA_H", "✎ ventana del filtro, en horas", vacio="None") + """

VENTANA_H = prepara_ventana(VENTANA_H)
f_B = media_movil(T_hora, VENTANA_H)
retraso_B_h = (int(VENTANA_H) - 1) / 2
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(np.arange(HORAS) / 24, T_hora, color="#BBBBBB", lw=0.5, label="horaria")
ax.plot(np.arange(HORAS) / 24, f_B, color="#1F5FAD", lw=1.5, label=f"promedio móvil de {VENTANA_H:g} h")
ax.set_xlabel("día"); ax.set_ylabel("T (°C)"); ax.set_xticks(range(0, 61, 5)); ax.grid(alpha=0.3); ax.legend(fontsize=8)
titulo(ax, f"Ventana de {VENTANA_H:g} h", alumno)
firma(fig, alumno); plt.show()
print(f"Retraso del filtro: ({VENTANA_H:g} − 1) / 2 = {retraso_B_h:.1f} h")
revisa_ventana(VENTANA_H)
"""),
          cu.md("""
### B3 · Predicción con dos semanas
El cuaderno calcula el promedio de la **primera** y de la **última** semana. Con la fórmula del ★, calcula la
tendencia `m_pred` en °C/día: entre el centro de una semana y el de la otra hay `DIAS_SEM` = 53 días.
"""),
          cu.code("""
globals().update(tendencia_clima(T_hora))
print(f"Promedio de la primera semana: T_SEM1 = {T_SEM1:.2f} °C · de la última: T_SEM2 = {T_SEM2:.2f} °C · "
      f"DIAS_SEM = {DIAS_SEM}")
"""),
          cu.code(h("m_pred", "✎ tu tendencia predicha, en °C/día") + "\n\ncompleta(m_pred, 'la tendencia predicha')\n"
                  "print(f'Predicción: {m_pred:.3g} °C/día')"),
          cu.md("""
### B4 · La tendencia de los 60 días
El cuaderno calcula los 60 promedios diarios y les ajusta una recta por **mínimos cuadrados** (sesión 3). Su pendiente
es la tendencia obtenida, `m_obt`. Con ella estima cuántos días faltan, desde el final del registro, para que el promedio
diario llegue a 26 °C. La recta sólo vale **cerca de los datos**: la temperatura de la estación es un ciclo anual (sube
hasta mayo y baja con las lluvias), así que no se extrapola más de 30 días.

En la gráfica, la línea del promedio móvil va unas horas detrás de los puntos de cada día: es el retraso que calculaste.
"""),
          cu.code("""
m_obt = M_OBT
dias_limite_B = dias_al_limite(M_OBT, B_OBT)
RESULTADOS = {"m_tend": m_tend, "dias_limite": dias_limite, "sigma_f": sigma_f, "retraso_min": retraso_min,
              "ventana_h": VENTANA_H, "retraso_B_h": retraso_B_h, "m_pred": m_pred, "m_obt": m_obt,
              "s_clima": S_CLIMA, "dias_sobre_26": DIAS_SOBRE, "dias_limite_B": dias_limite_B}
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(np.arange(HORAS) / 24, T_hora, color="#DDDDDD", lw=0.5, label="horaria")
ax.plot(np.arange(HORAS) / 24, f_B, color="#9DB7D5", lw=1.2, label=f"promedio móvil de {VENTANA_H:g} h")
ax.plot(DIAS, T_DIARIA, "o", color="#1F5FAD", ms=4, label="promedio de cada día")
ax.plot(DIAS, M_OBT * DIAS + B_OBT, color="#C62828", lw=2, label=f"recta: {m_obt:.3g} °C/día")
ax.hlines([T_SEM1, T_SEM2], [0, 53], [7, 60], color="#D9822B", lw=3, label=f"semanas: {m_pred:.3g} °C/día")
ax.set_xlabel("día"); ax.set_ylabel("T (°C)"); ax.set_xticks(range(0, 61, 5)); ax.grid(alpha=0.3)
ax.legend(fontsize=8, ncol=2, loc="upper left")
titulo(ax, "Tendencia de 60 días", alumno)
firma(fig, alumno, RESULTADOS); plt.show()
print(f"Tendencia obtenida: {m_obt:.3g} °C/día · predicha con dos semanas: {m_pred:.3g} °C/día")
print(f"Componentes del registro · ciclo día–noche: ±{CICLO_B:.1f} °C en promedio · clima de cada semana: los promedios "
      f"diarios se separan de la recta {S_CLIMA:.2f} °C (desviación estándar) · tendencia: {m_obt:.3g} °C/día")
print(f"Días con promedio sobre 26 °C en tu registro: {DIAS_SOBRE}")
print("Días para que la recta llegue a 26 °C de promedio: " +
      ({-1: "más de 30 días o la tendencia no sube; la recta no lo puede decir", 0: "ya lo rebasa"}.get(
          dias_limite_B, f"{dias_limite_B:.0f}")))
"""),
          cu.md("""
### B5 · Conclusión
¿Coincide la tendencia que predijiste con dos semanas con la de los 60 días? ¿Por qué pueden diferir y cuál usarías
para programar una revisión de los gabinetes? Al menos 25 palabras, con tus dos tendencias.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'tu tendencia predicha': m_pred, 'la tendencia obtenida': m_obt}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S5_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
ruta = f"S5_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"dia": DIAS, "T_promedio_diario": np.round(T_DIARIA, 2), "T_tendencia": np.round(M_OBT * DIAS + B_OBT, 2)},
             extra={"fuente": FUENTE, "periodo": f"{inicio} a {fin}", "equipo": LUGAR})
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
# Sólo profesor · Clave del grupo y verificación de los CSV
1. Pega en `CODIGOS` la lista de códigos del grupo y ejecuta: la tabla da los resultados esperados de la parte A.
2. Sube los CSV entregados y ejecuta la última celda. Para la parte B la celda vuelve a leer los 60 días de cada
   alumno (primero de la copia del repositorio) y recalcula su tendencia; si la fuente del CSV no es la misma, lo dice.
   Tolerancia: 2 %.
"""),
              cu.code('''
import glob
CODIGOS = """
217654321
219876543
""".split()
filas = []
for c in CODIGOS:
    a = identificar("Alumno Clave", c, SESION)
    d, k_ = datos_s5(a), clave_s5(a)
    filas.append({"codigo": c, "equipo": d["LUGAR"], "T_DIA1": d["T_DIA1"], "T_DIA_ULT": d["T_DIA_ULT"],
                  "LIMITE": d["LIMITE"], "N_VENT": d["N_VENT"], "DT_MIN": d["DT_MIN"],
                  **{x: round(float(v), 4) for x, v in k_.items()}})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
def _difiere(x, ref):
    return abs(x - ref) > 0.02 * max(abs(ref), 1e-3)

for ruta in sorted(glob.glob("S5_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    a = identificar("Alumno Clave", meta["codigo"], SESION)
    k_ = clave_s5(a)
    malos = [x for x in k_ if x not in res or _difiere(res[x], k_[x])]
    T_, fuente_, _, _ = carga_clima(a, primero_copia=True)
    if fuente_.split(" ·")[0] != str(meta.get("fuente", "")).split(" ·")[0]:
        malos.append(f"fuente ({meta.get('fuente')} en el CSV, {fuente_} ahora)")
    else:
        t_ = tendencia_clima(T_)
        esperado = {"m_obt": t_["M_OBT"], "m_pred": (t_["T_SEM2"] - t_["T_SEM1"]) / DIAS_SEM,
                    "dias_limite_B": dias_al_limite(t_["M_OBT"], t_["B_OBT"]), "dias_sobre_26": t_["DIAS_SOBRE"]}
        malos += [x for x, v in esperado.items() if x not in res or _difiere(res[x], v)]
    if res.get("ventana_h", 1) % 24 or _difiere(res.get("retraso_B_h", -9), (res.get("ventana_h", 0) - 1) / 2):
        malos.append("ventana")
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · "
          f"fuente {meta.get('fuente')} · ventana {res.get('ventana_h', 0):g} h · "
          + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("m_tend", "★ Tendencia de tu equipo (°C/día)", "0.0000"),
                    ("dias_limite", "Días para llegar al límite (parte A)", "0.0"),
                    ("sigma_f", "Ruido después del filtro (°C)", "0.0000"),
                    ("retraso_min", "Retraso del filtro (min)", "0.0"),
                    ("ventana_h", "Ventana elegida en la práctica (h)", "0"),
                    ("retraso_B_h", "Retraso de esa ventana (h)", "0.0"),
                    ("m_pred", "Tendencia predicha con dos semanas (°C/día)", "0.0000"),
                    ("m_obt", "Tendencia obtenida con 60 días (°C/día)", "0.0000"),
                    ("s_clima", "Separación de los promedios diarios respecto a la recta (°C)", "0.00"),
                    ("dias_sobre_26", "Días con promedio sobre 26 °C", "0"),
                    ("dias_limite_B", "Días para que la recta llegue a 26 °C (0: ya lo rebasa; −1: más de 30)", "0")],
        comparacion=("m_obt", "m_pred", "Error de la predicción con dos semanas respecto a la recta de 60 días (%)"),
        preguntas=["1. ¿Por qué tu ventana elimina el ciclo día–noche y qué precio pagas por ella? Usa tu ventana y "
                   "su retraso.",
                   "2. Con tu tendencia obtenida y los días con promedio sobre 26 °C, ¿cuándo programarías la revisión "
                   "preventiva de los gabinetes, y por qué dos semanas de datos no bastan para estimar la tendencia? "
                   "Usa tu separación respecto a la recta."],
        tabla={"encabezado_csv": "dia", "x": ("A", "Día"),
               "series": [("B", "Promedio diario"), ("C", "Tendencia")]},
        grafica={"titulo": "Promedios diarios y tendencia", "x": "Día", "y": "Temperatura (°C)",
                 "tipo": "dispersion"},
        renglones=60,
        metadatos=(("Fuente de los datos", "fuente"), ("Periodo", "periodo"), ("Equipo (parte A)", "equipo")),
        csv_ejemplo=csv_ejemplo)


if __name__ == "__main__":
    cu.guardar(celdas(), ALUMNO)
    cu.guardar(celdas(prof=True), PROF)
    generar_hoja()
    print("listo:", ALUMNO, PROF, HOJA, sep="\n  ")
    if len(sys.argv) == 3 and sys.argv[1] == "--prueba":
        cu.guardar(celdas(r="numero", nombre="Alumno De Prueba", codigo="217654321"),
                   os.path.join(sys.argv[2], f"{SESION}_numeros.ipynb"))
        ruta = cu.guardar(celdas(r=True, nombre="Alumno De Prueba", codigo="217654321"),
                          os.path.join(sys.argv[2], "S5_resuelto.ipynb"))
        print("  prueba:", ruta)
