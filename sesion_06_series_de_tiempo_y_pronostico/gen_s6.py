"""Sesión 6 · Series de tiempo y pronóstico. Genera:

    S6_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S6_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S6_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s6.py            -> los tres archivos
      python gen_s6.py --prueba D -> además, una versión resuelta en D para ejecutarla

Parte A: PM10 diario sintético de la toma de aire exterior de un cuarto limpio, proceso AR(1) con parámetros por
código. Parte B: SIMAJ 2022 (Sistema de Monitoreo Atmosférico de Jalisco), datos públicos reales, en
datos/datos_2022.xlsx; estación y ventana de prueba por código (33 ventanas con 60 días de entrenamiento casi completos).
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S6"
CARPETA = "sesion_06_series_de_tiempo_y_pronostico"
ALUMNO = os.path.join(AQUI, "S6_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S6_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S6_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S6_AC_CLASE_Colab_ALUMNO.ipynb"
URL_XLSX = "https://raw.githubusercontent.com/ggt13/DAQ_TSU/main/" + CARPETA + "/datos/datos_2022.xlsx"

DATOS_S6 = f'URL_XLSX = "{URL_XLSX}"\n' + r'''
import warnings
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
warnings.filterwarnings("ignore", module="statsmodels")

LIMITE = 50.0                # µg/m³, PM10 promedio de 24 h: valor final de la NOM-025-SSA1-2021 (en 2022 regía 70)
HORAS_MIN = 18               # 75 % de 24 h: mínimo de horas válidas para un promedio diario
DIAS_ENTRENA, DIAS_PRUEBA = 60, 14
UNIDADES_PM = ["µg/m", "μg/m", "ug/m", "UG/M", "Ug/m", "microgramo"]   # µ (micro) o μ (griega); m3, m³ o m^3
CODIGOS_SIMAJ = ["IF", "ND", "IR", "IO"]
VENTANAS = [  # estación y primer día de prueba; 60 días de entrenamiento con al menos 52 promedios válidos
    ("Aguilas", "2022-03-02"), ("Tlaquepaque", "2022-03-02"), ("Centro", "2022-03-02"), ("Santa Fe", "2022-03-02"),
    ("Las Pintas", "2022-03-02"), ("Tlaquepaque", "2022-03-09"), ("Centro", "2022-03-09"),
    ("Tlaquepaque", "2022-03-16"), ("Tlaquepaque", "2022-03-23"), ("Santa Fe", "2022-03-30"),
    ("Centro", "2022-03-30"), ("Tlaquepaque", "2022-03-30"), ("Tlaquepaque", "2022-04-06"), ("Aguilas", "2022-04-06"),
    ("Las Pintas", "2022-04-13"), ("Centro", "2022-04-13"), ("Santa Fe", "2022-04-13"), ("Miravalle", "2022-04-27"),
    ("Miravalle", "2022-05-04"), ("Centro", "2022-05-11"), ("Miravalle", "2022-05-11"), ("Aguilas", "2022-05-11"),
    ("Las Pintas", "2022-05-18"), ("Centro", "2022-05-18"), ("Santa Fe", "2022-05-18"), ("Aguilas", "2022-06-01"),
    ("Aguilas", "2022-06-22"), ("Las Pintas", "2022-07-13"), ("Las Pintas", "2022-08-17"), ("Aguilas", "2022-09-28"),
    ("Santa Fe", "2022-11-23"), ("Santa Fe", "2022-12-07"), ("Las Pintas", "2022-12-14"),
]
ORDENES = [(1, 0, 0), (2, 0, 0), (3, 0, 0), (0, 0, 1), (1, 0, 1), (2, 0, 1)]   # candidatos, todos con d = 0
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def fecha(t):
    return f"{t.day} {MESES[t.month - 1]}"


def mae(e):
    return float(np.nanmean(np.abs(e)))


def rmse(e):
    return float(np.sqrt(np.nanmean(np.asarray(e, float) ** 2)))


def datos_s6(alumno):
    """Parte A: 40 días de PM10 diario en la toma de aire exterior, un proceso AR(1) personal, y un día hora por hora."""
    mu = parametro(alumno, "mu", 30, 60, 1)
    phi = parametro(alumno, "phi", 0.35, 0.8, 2)
    sig = parametro(alumno, "sigma", 6, 14, 2)
    g = alumno.rng("serie")
    x = [mu]
    for _ in range(45):
        x.append(mu + phi * (x[-1] - mu) + g.normal(0, sig))
    x = np.round(np.clip(np.array(x[6:]), 5, None), 1)          # 40 días; se descartan los primeros 6
    real = x[30:35]                                             # la semana pasada: días 31 a 35
    pron = np.round(mu + phi * (x[29:34] - mu), 1)              # pronóstico AR(1) de cada día con el día anterior
    pers = x[29:34]                                             # persistencia: mañana igual que hoy
    # un día hora por hora, con huecos marcados con códigos del SIMAJ
    h = np.arange(24)
    horas = np.round(np.clip(x[-1] * (1 + 0.35 * np.sin(2 * np.pi * (h - 14) / 24))
                             + alumno.rng("horas").normal(0, 4, 24), 2, None), 1).astype(object)
    n_hue = asignar(alumno, [3, 4, 5, 6, 7, 8, 9], salto=1)
    huecos = alumno.rng("huecos").choice(24, n_hue, replace=False)
    for k, i in enumerate(sorted(huecos)):
        horas[i] = CODIGOS_SIMAJ[(int(alumno.codigo) + k) % len(CODIGOS_SIMAJ)]
    validas = np.array([v for v in horas if not isinstance(v, str)], float)
    return dict(MU_A=mu, PHI_A=phi, SERIE_A=x, X_HOY=float(x[-1]), REAL_A=real, PRON_A=pron, PERS_A=pers,
                HORAS_A=list(horas), N_VAL=int(validas.size), SUMA_VAL=round(float(validas.sum()), 1))


def clave_s6(alumno):
    """Resultados esperados de la parte A."""
    d = datos_s6(alumno)
    e = d["REAL_A"] - d["PRON_A"]
    return {"pron_A": d["MU_A"] + d["PHI_A"] * (d["X_HOY"] - d["MU_A"]), "mae_A": mae(e), "rmse_A": rmse(e),
            "prom_A": d["SUMA_VAL"] / d["N_VAL"]}


def carga_simaj(alumno):
    """El archivo del SIMAJ 2022 (≈ 7 MB): del repositorio, o el que subió el alumno. Si nada funciona, sintéticos."""
    for origen in (URL_XLSX, "datos_2022.xlsx"):
        try:
            crudo = pd.read_excel(origen, sheet_name="SIMAJ2022")
            return crudo, "SIMAJ 2022 (Gobierno de Jalisco), datos públicos"
        except Exception as e:
            print(f"⚠ No se pudo leer {origen}: {type(e).__name__}")
    print("⚠ Sube datos_2022.xlsx con el ícono de carpeta y vuelve a ejecutar. Mientras tanto se usan datos SINTÉTICOS.")
    est, ini = asignar(alumno, VENTANAS)
    t = pd.date_range("2022-01-01", "2022-12-31 23:00", freq="h")
    g = alumno.rng("simaj")
    dia = np.zeros(365)
    for i in range(1, 365):
        dia[i] = 0.5 * dia[i - 1] + g.normal(0, 12)
    pm = np.clip(55 + np.repeat(dia, 24) + 10 * np.sin(2 * np.pi * (t.hour - 14) / 24) + g.normal(0, 6, t.size), 3, None)
    pm = np.round(pm, 1).astype(object)
    pm[g.random(t.size) < 0.1] = "IF"
    crudo = pd.DataFrame({"Estacion": est, "Date_Time": t, "Hora": t.strftime("%H:%M:%S"), "PM10": pm})
    return crudo, "SINTÉTICOS (sin el archivo del SIMAJ)"


def limpia_estacion(crudo, estacion, variable="PM10"):
    """Fecha + hora, duplicados fuera, códigos a vacío, interpolación de huecos de hasta 3 h y promedio diario (≥ 18 h)."""
    g = crudo[crudo["Estacion"] == estacion].copy()
    rep_dt = int(g.duplicated("Date_Time").sum())
    g["t"] = pd.to_datetime(pd.to_datetime(g["Date_Time"]).dt.strftime("%Y-%m-%d") + " " + g["Hora"].astype(str))
    rep_t = int(g.duplicated("t").sum())
    g = g.drop_duplicates("t").set_index("t").sort_index()
    x = pd.to_numeric(g[variable], errors="coerce")
    codigos = g[variable][x.isna() & g[variable].notna()].astype(str).str.strip().value_counts()
    hueco = x.isna()
    largo = hueco.groupby((hueco != hueco.shift()).cumsum()).transform("sum")
    xi = x.interpolate(limit_area="inside").where(~hueco | (largo <= 3))
    n = x.resample("D").count()
    diario = x.resample("D").mean().where(n >= HORAS_MIN)
    return dict(x=x, xi=xi, diario=diario, rep_dt=rep_dt, rep_t=rep_t, codigos=codigos,
                vacias=int(g[variable].isna().sum()), interpoladas=int(xi.notna().sum() - x.notna().sum()))


def ventana_b(diario, inicio):
    """Entrenamiento (60 días) y prueba (14 días) a partir del primer día de prueba."""
    ini = pd.Timestamp(inicio)
    entrena = diario[ini - pd.Timedelta(days=DIAS_ENTRENA): ini - pd.Timedelta(days=1)]
    prueba = diario[ini: ini + pd.Timedelta(days=DIAS_PRUEBA - 1)]
    return entrena, prueba


def ajusta(entrena, orden):
    return ARIMA(entrena.values, order=orden).fit()


def tabla_aic(entrena):
    return {o: float(ajusta(entrena, o).aic) for o in ORDENES}


def pronostico(modelo, entrena, prueba):
    """Un día adelante durante la prueba: cada pronóstico usa sólo los días anteriores; el modelo no se reajusta."""
    todo = np.concatenate([entrena.values, prueba.values])
    return modelo.apply(todo).predict(start=len(entrena), end=len(todo) - 1)


def revisa_orden(p, q, aic):
    """El orden elegido debe ser uno de los candidatos y el de menor AIC."""
    if p is None or q is None:
        raise ValueError("Escribe P_ORD y Q_ORD, el orden que elegiste.")
    o = (int(p), 0, int(q))
    faltan = []
    if o not in aic:
        faltan.append(f"({int(p)}, 0, {int(q)}) no está en la tabla")
    elif aic[o] > min(aic.values()) + 2:
        faltan.append(f"({int(p)}, 0, {int(q)}) tiene un AIC más de 2 unidades arriba del menor")
    REGISTRO["Orden del modelo"] = not faltan
    if faltan:
        raise ValueError("Orden del modelo: " + "; ".join(faltan) + ".")
    print(f"✔ Orden elegido: ARIMA({int(p)}, 0, {int(q)}), AIC = {aic[o]:.1f}")


def revisa_veredicto(v, n_val):
    """¿El día cuenta? Válido si tiene al menos HORAS_MIN horas medidas."""
    t = str(v).strip().lower().replace("á", "a")
    if t not in ("valido", "no valido"):
        raise ValueError('Escribe VEREDICTO = "válido" o VEREDICTO = "no válido".')
    ok = (t == "valido") == (n_val >= HORAS_MIN)
    REGISTRO["Validez del día"] = ok
    if not ok:
        raise ValueError("Validez del día: revisa cuántas horas medidas tiene tu día y el mínimo de la norma.")
    print("✔ Validez del día revisada.")


def comunes(real, *prons):
    """Días de prueba donde el valor real y todos los pronósticos existen: ahí se comparan los errores."""
    ok = ~np.isnan(np.asarray(real, float))
    for x in prons:
        ok &= ~np.isnan(np.asarray(x, float))
    return ok
'''

SOL = {
    "pron_A": "MU_A + PHI_A * (X_HOY - MU_A)",
    "SUST_1": 'f"{MU_A} + {PHI_A} × ({X_HOY} − {MU_A}) = {pron_A:.4g} µg/m³"',
    "PRED_1": '"mañana el polvo regresa hacia el promedio de la toma de aire pero conserva parte de lo que pasó hoy"',
    "mae_A": "np.mean(np.abs(REAL_A - PRON_A))",
    "SUST_2": 'f"(|{REAL_A[0]} − {PRON_A[0]}| + … ) / 5 = {mae_A:.4g} µg/m³"',
    "PRED_2": '"en promedio el pronóstico de un día se equivoca esta cantidad y con eso decido cuánto margen dejar"',
    "rmse_A": "np.sqrt(np.mean((REAL_A - PRON_A) ** 2))",
    "SUST_3": 'f"√[(({REAL_A[0]} − {PRON_A[0]})² + … ) / 5] = {rmse_A:.4g} µg/m³"',
    "PRED_3": '"si el RMSE es mucho mayor que el MAE hubo algún día con un error grande que el promedio esconde"',
    "prom_A": "SUMA_VAL / N_VAL",
    "SUST_4": 'f"{SUMA_VAL} / {N_VAL} = {prom_A:.4g} µg/m³"',
    "PRED_4": '"las horas con código no cuentan y el día sólo se usa en el modelo si tiene al menos dieciocho horas medidas"',
    "VEREDICTO": '"válido" if N_VAL >= HORAS_MIN else "no válido"',
    "CIERRE": ('f"La semana pasada el AR(1) tuvo un MAE de {mae_A:.3g} µg/m³ y la persistencia {MAE_PERS_A:.3g} µg/m³; '
               'esta vez {\'ganó el AR(1)\' if mae_A < MAE_PERS_A else \'ganó la persistencia\'}, pero con cinco días '
               'un solo error grande cambia el resultado"'),
    "PRON_DIA1": "MU_B + PHI_B * (X_ULT_B - MU_B)",
    "P_ORD": "min([o for o in AIC_B if AIC_B[o] <= min(AIC_B.values()) + 2], key=lambda o: (o[0] + o[2], AIC_B[o]))[0]",
    "Q_ORD": "min([o for o in AIC_B if AIC_B[o] <= min(AIC_B.values()) + 2], key=lambda o: (o[0] + o[2], AIC_B[o]))[2]",
    "CONCLUSION_B": ('f"Con ARIMA({P_ORD}, 0, {Q_ORD}) el MAE de los días de prueba fue {mae_mod:.3g} µg/m³ y con '
                     'persistencia {mae_pers:.3g} µg/m³, así que {\'el modelo sí\' if mae_mod < mae_pers else \'el modelo no\'} '
                     'le ganó; para programar la revisión de prefiltros sumaría ese error al pronóstico como margen"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# S6 · Series de tiempo y pronóstico · ¿Cuánto polvo habrá mañana?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Preparar una **serie de tiempo** real (códigos en lugar de números, fechas repetidas, horas faltantes, promedios
diarios válidos), **pronosticar** el día siguiente con un modelo autorregresivo y decidir con su **error** (MAE y
RMSE) si el pronóstico sirve para una decisión de mantenimiento **predictivo**.

## La situación
La manejadora de aire de un cuarto limpio toma aire de afuera a través de prefiltros. Cuando el polvo exterior
(**PM10**, partículas de diámetro aerodinámico de hasta 10 µm) sube, los prefiltros se cargan antes y su presión
diferencial (ΔP) crece: si se sabe un día antes, se programa la revisión y se evita un paro. La variable que decide
el cambio es la ΔP del prefiltro; el PM10 de afuera es un **indicador indirecto** que permite anticiparla. El límite
de 50 µg/m³ que usamos como umbral de ejemplo es de salud pública, no de mantenimiento. En clase pronosticas el PM10 de **tu** toma de aire
(datos sintéticos con tus parámetros); en la práctica, el de una estación real del Sistema de Monitoreo Atmosférico
de Jalisco (SIMAJ), con los datos de 2022 tal como los publica el gobierno.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero): el pronóstico de mañana, el MAE y el RMSE de la semana pasada, y un promedio diario válido. En cada uno escribes tu resultado, la sustitución con tus números y su unidad, y lo que predice | Tu pronóstico y cuánto confiar en él |
| **B · Práctica** | 80 min | Limpias el archivo real de tu estación, pronosticas a mano el primer día, eliges el modelo por su AIC y comparas sus errores contra la persistencia en 14 días | Gráficas firmadas, tu conclusión y el archivo `S6_<código>.csv` |
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
         cu.herramientas(DATOS_S6)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** toma de aire: el modelo que describe su PM10 diario, el valor de hoy, lo que pasó la
semana pasada y otro día (el martes pasado) hora por hora.

**El modelo AR(1).** El PM10 de mañana **regresa hacia el promedio** μ, pero conserva una fracción φ de lo que hoy
se aparta de él: **x̂(mañana) = μ + φ · (x(hoy) − μ)**. Con φ = 0 el pronóstico siempre es el promedio; con φ = 1
es la **persistencia** (mañana igual que hoy).

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
pron_A = 47.0
SUST_1 = "40 + 0.5 × (54 − 40) = 47.0 µg/m³"
PRED_1 = "mañana el polvo baja un poco hacia el promedio aunque hoy fue un día alto"
```
Para la unidad basta escribir **ug/m3** (también se acepta µg/m³).
"""),
          cu.code("""
globals().update(datos_s6(alumno))
print("Tu toma de aire exterior · PM10 promedio de 24 h, en µg/m³")
print(f"  Modelo AR(1): MU_A = {MU_A} µg/m³ · PHI_A = {PHI_A} · hoy: X_HOY = {X_HOY} µg/m³")
print("\\n  La semana pasada (5 días):")
print("    real:       ", "  ".join(f"{v:5.1f}" for v in REAL_A))
print("    pronóstico: ", "  ".join(f"{v:5.1f}" for v in PRON_A))
print("\\n  El martes pasado, hora por hora (los códigos IF, ND, IR e IO no son mediciones):")
print("    " + "  ".join(f"{i:02d}h:{v}" for i, v in enumerate(HORAS_A[:12])))
print("    " + "  ".join(f"{i + 12:02d}h:{v}" for i, v in enumerate(HORAS_A[12:])))
print(f"  Suma de las horas con número: SUMA_VAL = {SUMA_VAL} µg/m³ (cuántas son, lo cuentas tú)")
"""),
          cu.md("""
### ★ Ejercicio 1 · El pronóstico de mañana (3 pts)
**Para qué sirve:** es el número con el que se decide hoy si mañana se revisan los prefiltros.

Con tu modelo: **x̂ = μ + φ · (x(hoy) − μ)**. Calcula `pron_A` en µg/m³.
"""),
          cu.ejercicio(h, 1, "pron_A", [("tu μ", "MU_A"), ("tu φ", "PHI_A"), ("tu valor de hoy", "X_HOY")],
                       "UNIDADES_PM"),
          cu.md("""
### Ejercicio 2 · ¿Cuánto se equivoca en promedio? MAE (2 pts)
**Para qué sirve:** dice cuánto margen dejar alrededor del pronóstico.

El **error medio absoluto** (MAE) es el promedio de los errores **sin signo**: resta real − pronóstico de cada día de
la semana pasada, quita el signo y promedia los cinco. Resultado en µg/m³.

Conviene una tablita en papel o en tu hoja de cálculo con cinco renglones y las columnas real · pronóstico · error ·
|error| · error²; la última columna sirve para el ejercicio 3. Los números impresos ya vienen redondeados a una décima:
úsalos tal cual.
"""),
          cu.ejercicio(h, 2, "mae_A", [("tu primer valor real", "REAL_A[0]"), ("tu primer pronóstico", "PRON_A[0]")],
                       "UNIDADES_PM"),
          cu.md("""
### Ejercicio 3 · ¿Hubo algún error grande? RMSE (2 pts)
**Para qué sirve:** el RMSE castiga más los errores grandes; si sale mucho mayor que el MAE, algún día falló feo.

La **raíz del error cuadrático medio**: eleva al cuadrado cada error de la semana pasada, promedia los cinco y saca
raíz cuadrada. Resultado en µg/m³.
"""),
          cu.ejercicio(h, 3, "rmse_A", [("tu primer valor real", "REAL_A[0]"), ("tu primer pronóstico", "PRON_A[0]")],
                       "UNIDADES_PM"),
          cu.md("""
### Ejercicio 4 · Un promedio diario válido (2 pts)
**Para qué sirve:** el modelo trabaja con promedios diarios; si se arman mal, el pronóstico hereda el error.

Los códigos (IF, ND, IR, IO) **no** son ceros: son horas sin medición y no se promedian. **Cuenta** cuántas de las 24
horas del martes pasado tienen número y calcula el promedio con `SUMA_VAL`. Después decide si el día **cuenta**: la
NOM-025-SSA1-2021 pide al menos 18 horas válidas (75 %); si tiene menos, el promedio se puede calcular, pero el día
queda vacío en la serie del modelo.
"""),
          cu.ejercicio(h, 4, "prom_A", [("tu suma de horas válidas", "SUMA_VAL"),
                                        ("el número de horas con número que contaste", "N_VAL")], "UNIDADES_PM"),
          cu.code(h("VEREDICTO", 'escribe "válido" o "no válido"') + "\n\nrevisa_veredicto(VEREDICTO, N_VAL)"),
          cu.code("""
MAE_PERS_A = mae(REAL_A - PERS_A)
dias = np.arange(1, SERIE_A.size + 1)
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(dias, SERIE_A, "o-", color="#9DB7D5", ms=3, label="PM10 diario")
ax.plot(dias[30:35], PRON_A, "s", color="#D9822B", ms=6, label=f"pronóstico AR(1), MAE {mae_A:.3g}")
ax.plot(dias[-1] + 1, pron_A, "*", color="#C62828", ms=14, label=f"mañana: {pron_A:.1f} µg/m³")
ax.axhline(MU_A, color="#666", lw=0.8, ls=":", label=f"μ = {MU_A}")
ax.axhline(LIMITE, color="#C62828", lw=1, ls="--", label=f"umbral de ejemplo {LIMITE:g}")
ax.set_xlabel("día"); ax.set_ylabel("PM10 (µg/m³)")
ax.legend(fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
titulo(ax, "Tu toma de aire", alumno)
fig.subplots_adjust(bottom=0.32)
firma(fig, alumno); plt.show()
print(f"MAE de la semana pasada · AR(1): {mae_A:.3g} µg/m³ · persistencia: {MAE_PERS_A:.3g} µg/m³ · "
      f"RMSE/MAE del AR(1) = {rmse_A / mae_A:.2f}")
"""),
          cu.md("""
### Cierre (1 pt)
¿Le ganó el AR(1) a la persistencia la semana pasada? Compara los dos MAE impresos arriba. Ojo: con sólo cinco días,
un error grande cambia el resultado; no basta para elegir un modelo para siempre. Al menos 20 palabras, con los dos
números.
"""),
          cu.code(h("CIERRE") + "\n\nrevisa_texto('Cierre', CIERRE, {'el MAE del AR(1)': mae_A,\n"
                  "             'el MAE de la persistencia': MAE_PERS_A})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** pasar de un archivo público «tal como llega» a un pronóstico evaluado.

El archivo del SIMAJ 2022 tiene 10 estaciones, 17 variables y una medición por hora (87 601 renglones). Cada alumno
trabaja con una estación y unas fechas distintas, según su código. Las columnas **no traen unidades**: hay que
buscarlas en la documentación de la fuente (el PM10 se reporta en µg/m³). Umbral de ejemplo: 50 µg/m³ en 24 h, el
valor final de la NOM-025-SSA1-2021 (en 2022 regía 70 µg/m³). Fuente: Sistema de Monitoreo Atmosférico de Jalisco,
Gobierno de Jalisco; al usar datos públicos se cita la fuente y se declara qué se descartó.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · El archivo tal como llega | 10 | Ves cuántas celdas son códigos y qué estaciones no sirven |
| B2 · Limpieza de tu estación | 15 | Fecha + hora, duplicados, códigos, huecos y promedios diarios válidos |
| B3 · Tu pronóstico a mano | 10 | Con μ y φ ajustados a tus 60 días, pronosticas el primer día de prueba |
| B4 · ¿Qué modelo? | 15 | Comparas seis modelos por su AIC y eliges uno |
| B5 · 14 días de prueba | 10 | Tu modelo contra la persistencia: MAE y RMSE |
| B6 · Conclusión | 10 | Decides si el pronóstico sirve, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
if "crudo" not in globals() or FUENTE.startswith("SINTÉTICOS"):   # se lee una sola vez (≈ 30 s)
    print("Leyendo el archivo del SIMAJ 2022 (≈ 7 MB)…")
    crudo, FUENTE = carga_simaj(alumno)
medidas = [c for c in crudo.columns if c not in ("Estacion", "Date_Time", "Hora")]
num = crudo[medidas].apply(pd.to_numeric, errors="coerce")
vacias = crudo[medidas].isna()
print(f"B1 · {len(crudo):,} renglones · {crudo['Estacion'].nunique()} estaciones · {len(medidas)} variables · fuente: {FUENTE}")
print(f"     Celdas de medición: {100 * num.notna().values.mean():.0f} % con número, "
      f"{100 * (~vacias & num.isna()).values.mean():.0f} % con código, {100 * vacias.values.mean():.0f} % vacías")
disp = crudo.assign(ok=pd.to_numeric(crudo["PM10"], errors="coerce").notna()).groupby("Estacion")["ok"].mean() * 100
disp = disp.sort_values()
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.barh(disp.index, disp.values, color=["#C62828" if v < 40 else "#D9822B" if v < 75 else "#2E7D32" for v in disp])
ax.bar_label(ax.containers[0], fmt="%.0f %%", fontsize=8, padding=2)
ax.axvline(75, color="#444", ls="--"); ax.set_xlabel("% de horas con PM10 válido en el año"); ax.set_xlim(0, 108)
titulo(ax, "Disponibilidad de PM10 por estación", alumno)
firma(fig, alumno); plt.tight_layout(rect=(0, 0.06, 1, 1)); plt.show()
sin = [e for e, v in disp.items() if v == 0]
if sin:
    print("Sin ningún dato de PM10 en todo el año:", ", ".join(sin))
"""),
          cu.md("""
### B2 · Limpieza de tu estación
La celda hace cinco pasos y dice qué encontró en cada uno. Léelos: los usarás en tu reporte.
1. **Fecha y hora.** En algunas estaciones la columna `Date_Time` trae sólo la fecha: se arma fecha + `Hora`.
2. **Duplicados.** Si después de eso una hora sigue repetida, se queda una.
3. **Códigos a vacío.** IF, ND, IR… no son números: se vuelven vacío, **no** cero.
4. **Huecos cortos.** Huecos de hasta 3 h se interpolan para dibujar la serie horaria; **no** cuentan para el 75 %.
5. **Promedio diario.** Vale si el día tiene al menos 18 horas medidas.
"""),
          cu.code("""
ESTACION, INICIO = asignar(alumno, VENTANAS)
L = limpia_estacion(crudo, ESTACION)
diario = L["diario"]
print(f"Tu estación: {ESTACION} · tu primer día de prueba: {fecha(pd.Timestamp(INICIO))} de 2022")
print(f"1. Renglones cuyo Date_Time se repite (traen sólo la fecha, sin hora): {L['rep_dt']} · repetidos con "
      f"fecha + hora: {L['rep_t']}")
print(f"2. Duplicados borrados: {L['rep_t']} · quedan {len(L['x'])} horas")
print(f"3. Horas con código: {int(L['codigos'].sum())} ({', '.join(f'{k}: {v}' for k, v in L['codigos'].head(6).items())}) "
      f"· vacías: {L['vacias']} · horas válidas: {100 * L['x'].notna().mean():.1f} %")
print(f"4. Horas interpoladas (huecos de hasta 3 h): {L['interpoladas']}")
print(f"5. Días con promedio válido: {int(diario.notna().sum())} de {len(diario)} · "
      f"días sobre {LIMITE:g} µg/m³: {int((diario > LIMITE).sum())}")
mensual = diario.resample("MS").mean()
print("6. Remuestreo a meses (promedio de los días válidos):",
      " · ".join(f"{MESES[t.month - 1]} {v:.0f}" for t, v in mensual.items() if not np.isnan(v)))
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
a1.plot(L["xi"].index, L["xi"].values, color="#9DB7D5", lw=0.4)
a1.set_ylabel("PM10 horario"); titulo(a1, f"{ESTACION}, 2022", alumno)
a2.plot(diario.index, diario.values, "o", ms=2.5, color="#1F5FAD")
a2.axhline(LIMITE, color="#C62828", ls="--", lw=1); a2.set_ylabel("PM10 diario (µg/m³)")
a2.axvspan(pd.Timestamp(INICIO) - pd.Timedelta(days=DIAS_ENTRENA), pd.Timestamp(INICIO), color="#DDD", alpha=0.6)
a2.axvspan(pd.Timestamp(INICIO), pd.Timestamp(INICIO) + pd.Timedelta(days=DIAS_PRUEBA), color="#F6D7B0", alpha=0.8)
a2.set_title("Gris: 60 días de entrenamiento · naranja: 14 días de prueba", fontsize=10)
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### B3 · Tu pronóstico a mano
El cuaderno ajusta un AR(1) a tus 60 días de entrenamiento e imprime μ, φ y el último día. Aquí μ es el **promedio
alrededor del cual oscila la serie** (como en el ★), no la constante c que aparece en otros libros como
x = c + φ·x. Calcula con la fórmula del ★ el pronóstico del **primer día de prueba**, `PRON_DIA1`, en µg/m³.
Después de ejecutar verás el valor real.
"""),
          cu.code("""
entrena, prueba = ventana_b(diario, INICIO)
ar1 = ajusta(entrena, (1, 0, 0))
MU_B, PHI_B = round(float(ar1.params[0]), 1), round(float(ar1.params[1]), 3)
X_ULT_B = round(float(entrena.iloc[-1]), 1)
print(f"Entrenamiento: {fecha(entrena.index[0])} a {fecha(entrena.index[-1])} · "
      f"{int(entrena.notna().sum())} días válidos de {DIAS_ENTRENA} (los que faltan, el modelo los tolera)")
print(f"AR(1) ajustado: MU_B = {MU_B} µg/m³ · PHI_B = {PHI_B} · último día: X_ULT_B = {X_ULT_B} µg/m³")
"""),
          cu.code(h("PRON_DIA1", "✎ tu pronóstico del primer día de prueba, en µg/m³") + """

completa(PRON_DIA1, "tu pronóstico del primer día")
REAL_DIA1 = round(float(prueba.iloc[0]), 1)
print(f"Tu pronóstico: {PRON_DIA1:.1f} µg/m³ · lo que midió la estación: {REAL_DIA1} µg/m³ · "
      f"error: {REAL_DIA1 - PRON_DIA1:+.1f} µg/m³")
"""),
          cu.md("""
### B4 · ¿Qué modelo?
El AR(1) usa sólo el día anterior. Otros modelos usan dos o tres días atrás (AR(2), AR(3)) o el error del pronóstico
anterior (la parte MA). Para elegir **sin mirar la prueba** se usa el **AIC** del entrenamiento: premia que el modelo
se ajuste y castiga que tenga más parámetros. **Menor es mejor**, pero diferencias de menos de 2 no distinguen dos
modelos: **entre los que quedan a menos de 2 del menor, elige el de menos parámetros** (p + q más chico). Escribe en
`P_ORD` y `Q_ORD` los números del modelo que elegiste; por ejemplo, para ARIMA(2, 0, 1) escribe `P_ORD = 2` y
`Q_ORD = 1`.

La **d** de ARIMA(p, **d**, q) indica cuántas veces se trabaja con las diferencias de un día al siguiente en lugar de
con los valores; se usa cuando la serie tiene una tendencia que no regresa a un promedio. El PM10 diario oscila
alrededor de un promedio, por eso aquí todos los candidatos tienen d = 0.
"""),
          cu.code("""
AIC_B = tabla_aic(entrena)
print("Modelo           AIC")
for o, v in sorted(AIC_B.items(), key=lambda kv: kv[1]):
    print(f"ARIMA({o[0]}, 0, {o[2]})   {v:8.1f}")
"""),
          cu.code(h("P_ORD", "✎ p del modelo que elegiste", vacio="None") + "\n" +
                  h("Q_ORD", "✎ q del modelo que elegiste", vacio="None") + """

revisa_orden(P_ORD, Q_ORD, AIC_B)
P_ORD, Q_ORD = int(P_ORD), int(Q_ORD)
"""),
          cu.md("""
### B5 · 14 días de prueba
Cada día de prueba se pronostica con los días anteriores, sin volver a ajustar el modelo. La **persistencia**
(mañana igual que hoy) es la vara para medir: un modelo que no le gana no sirve.
"""),
          cu.code("""
modelo = ajusta(entrena, (P_ORD, 0, Q_ORD))
pron = pronostico(modelo, entrena, prueba)
real = prueba.values
pers = np.concatenate([[entrena.values[-1]], real[:-1]])
ok = comunes(real, pron, pers)                    # días con valor real y con los dos pronósticos
mae_mod, rmse_mod = mae(real[ok] - pron[ok]), rmse(real[ok] - pron[ok])
mae_pers, rmse_pers = mae(real[ok] - pers[ok]), rmse(real[ok] - pers[ok])
acierto_mod = int(np.sum((pron[ok] > LIMITE) == (real[ok] > LIMITE)))
acierto_pers = int(np.sum((pers[ok] > LIMITE) == (real[ok] > LIMITE)))
n_val = int(ok.sum())
RESULTADOS = {"pron_A": pron_A, "mae_A": mae_A, "rmse_A": rmse_A, "prom_A": prom_A,
              "mu_B": MU_B, "phi_B": PHI_B, "x_ult_B": X_ULT_B, "pron_dia1": PRON_DIA1, "real_dia1": REAL_DIA1,
              "p_ord": P_ORD, "q_ord": Q_ORD, "mae_mod": mae_mod, "rmse_mod": rmse_mod,
              "mae_pers": mae_pers, "rmse_pers": rmse_pers}
cola = entrena[-21:]
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(cola.index, cola.values, "o-", color="#9DB7D5", ms=4, label="entrenamiento")
ax.plot(prueba.index, real, "o-", color="#1F5FAD", ms=5, label="real")
ax.plot(prueba.index, pers, "x--", color="#888", ms=6, label=f"persistencia, MAE {mae_pers:.3g}")
ax.plot(prueba.index, pron, "s-", color="#D9822B", ms=5, label=f"ARIMA({P_ORD}, 0, {Q_ORD}), MAE {mae_mod:.3g}")
ax.axhline(LIMITE, color="#C62828", ls="--", lw=1)
ax.set_ylabel("PM10 diario (µg/m³)"); ax.legend(fontsize=8, ncol=2, loc="upper left")
ax.set_xticks(list(cola.index[::7]) + list(prueba.index[::3])); ax.set_xticklabels(
    [fecha(t) for t in list(cola.index[::7]) + list(prueba.index[::3])], fontsize=8)
titulo(ax, f"Pronóstico un día adelante · {ESTACION}", alumno)
firma(fig, alumno, RESULTADOS); plt.show()
print(f"Se comparan {n_val} días de prueba (los que tienen valor real y los dos pronósticos).")
print(f"ARIMA({P_ORD}, 0, {Q_ORD}): MAE {mae_mod:.3g} · RMSE {rmse_mod:.3g} µg/m³ · "
      f"aciertos arriba/abajo del umbral de ejemplo ({LIMITE:g}): {acierto_mod} de {n_val}")
print(f"Persistencia:    MAE {mae_pers:.3g} · RMSE {rmse_pers:.3g} µg/m³ · aciertos: {acierto_pers} de {n_val}")
"""),
          cu.md("""
### B6 · Conclusión
¿Le ganó tu modelo a la persistencia? ¿Usarías este pronóstico para programar la revisión de los prefiltros, sabiendo
cuánto se equivoca? Una regla práctica es actuar cuando **pronóstico + MAE** pasa el umbral. Al menos 25 palabras,
con los dos MAE.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'el MAE de tu modelo': mae_mod, 'el MAE de la persistencia': mae_pers}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S6_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
dias_rel = np.arange(-len(cola), DIAS_PRUEBA)
reales = np.concatenate([cola.values, real])
prons = np.concatenate([np.full(len(cola), np.nan), pron])
ruta = f"S6_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"dia": dias_rel,
              "PM10_real": ["" if np.isnan(v) else round(float(v), 1) for v in reales],
              "PM10_pronostico": ["" if np.isnan(v) else round(float(v), 1) for v in prons]},
             extra={"fuente": FUENTE, "estacion": ESTACION, "periodo": f"prueba desde {INICIO}"})
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
1. Pega en `CODIGOS` la lista de códigos del grupo y ejecuta: la tabla da los resultados esperados de la parte A y la
   estación de cada alumno.
2. Sube los CSV entregados y ejecuta la última celda: rehace la limpieza y los modelos de cada alumno con el mismo
   archivo y compara. El orden que declaró el alumno se acepta si su AIC queda a menos de 2 del menor; los errores se
   recalculan con ese orden. Tolerancia: 2 %.
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
    d, k_ = datos_s6(a), clave_s6(a)
    est, ini = asignar(a, VENTANAS)
    filas.append({"codigo": c, "MU_A": d["MU_A"], "PHI_A": d["PHI_A"], "X_HOY": d["X_HOY"], "estacion": est,
                  "inicio": ini, **{x: round(float(v), 3) for x, v in k_.items()}})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
def _difiere(x, ref):
    return abs(x - ref) > 0.02 * max(abs(ref), 1e-3)

for ruta in sorted(glob.glob("S6_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    a = identificar("Alumno Clave", meta["codigo"], SESION)
    k_ = clave_s6(a)
    malos = [x for x in k_ if x not in res or _difiere(res[x], k_[x])]
    est, ini = asignar(a, VENTANAS)
    if FUENTE.startswith("SINTÉTICOS") or str(meta.get("fuente", "")).startswith("SINTÉTICOS"):
        malos.append("fuente sintética: revisar la parte B a mano")
    elif meta.get("fuente") != FUENTE or meta.get("estacion") != est:
        malos.append(f"fuente o estación ({meta.get('fuente')}, {meta.get('estacion')})")
    else:
        en, pr = ventana_b(limpia_estacion(crudo, est)["diario"], ini)
        m1 = ajusta(en, (1, 0, 0))
        mu, ph, xu = round(float(m1.params[0]), 1), round(float(m1.params[1]), 3), round(float(en.iloc[-1]), 1)
        aic = tabla_aic(en)
        orden = (int(res.get("p_ord", -1)), 0, int(res.get("q_ord", -1)))
        if orden not in aic or aic[orden] > min(aic.values()) + 2:
            malos.append(f"orden {orden} fuera de los aceptables")
            orden = min(aic, key=aic.get)
        pron_ = pronostico(ajusta(en, orden), en, pr)
        pers_ = np.concatenate([[en.values[-1]], pr.values[:-1]])
        ok_ = comunes(pr.values, pron_, pers_)
        rv = pr.values[ok_]
        esperado = {"mu_B": mu, "phi_B": ph, "x_ult_B": xu, "pron_dia1": mu + ph * (xu - mu),
                    "real_dia1": round(float(pr.iloc[0]), 1),
                    "mae_mod": mae(rv - pron_[ok_]), "rmse_mod": rmse(rv - pron_[ok_]),
                    "mae_pers": mae(rv - pers_[ok_]), "rmse_pers": rmse(rv - pers_[ok_])}
        malos += [x for x, v in esperado.items() if x not in res or _difiere(res[x], v)]
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · {est} desde {ini} · "
          + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("pron_A", "★ Pronóstico de mañana en tu toma de aire (µg/m³)", "0.0"),
                    ("mae_A", "MAE de la semana pasada (µg/m³)", "0.00"),
                    ("rmse_A", "RMSE de la semana pasada (µg/m³)", "0.00"),
                    ("prom_A", "Promedio del martes pasado (µg/m³)", "0.0"),
                    ("mu_B", "μ del AR(1) de tu estación (µg/m³)", "0.0"),
                    ("phi_B", "φ del AR(1) de tu estación", "0.000"),
                    ("pron_dia1", "Tu pronóstico del primer día de prueba (µg/m³)", "0.0"),
                    ("real_dia1", "Lo que midió la estación ese día (µg/m³)", "0.0"),
                    ("p_ord", "p del modelo elegido por AIC", "0"),
                    ("q_ord", "q del modelo elegido por AIC", "0"),
                    ("mae_mod", "MAE de tu modelo, días de prueba (µg/m³)", "0.00"),
                    ("rmse_mod", "RMSE de tu modelo, días de prueba (µg/m³)", "0.00"),
                    ("mae_pers", "MAE de la persistencia, días de prueba (µg/m³)", "0.00"),
                    ("rmse_pers", "RMSE de la persistencia, días de prueba (µg/m³)", "0.00")],
        comparacion=("real_dia1", "pron_dia1", "Error de tu pronóstico del primer día respecto a lo medido (%)"),
        preguntas=["1. ¿Qué encontraste al limpiar tu estación (fechas, duplicados, códigos, días válidos), qué "
                   "habría pasado si los códigos se hubieran tomado como ceros y cómo citarías la fuente de los datos?",
                   "2. ¿Tu modelo le ganó a la persistencia? ¿Usarías su pronóstico (más su MAE como margen) para "
                   "programar la revisión de los prefiltros? Usa tus MAE y RMSE."],
        tabla={"encabezado_csv": "dia", "x": ("A", "Día (0 = primer día de prueba)"),
               "series": [("B", "Real"), ("C", "Pronóstico")]},
        grafica={"titulo": "PM10 diario: real y pronóstico un día adelante", "x": "Día", "y": "PM10 (µg/m³)",
                 "tipo": "dispersion"},
        renglones=40,
        metadatos=(("Fuente de los datos", "fuente"), ("Estación", "estacion"), ("Periodo", "periodo")),
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
                          os.path.join(sys.argv[2], "S6_resuelto.ipynb"))
        print("  prueba:", ruta)
