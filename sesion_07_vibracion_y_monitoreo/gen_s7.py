"""Sesión 7 · Monitoreo basado en condición: vibración. Genera:

    S7_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S7_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S7_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s7.py            -> los tres archivos
      python gen_s7.py --prueba D -> además, una versión resuelta en D para ejecutarla

Parte A: una máquina rotatoria y su rodamiento, con parámetros por código (velocidad, geometría, desbalance, línea
base). Parte B: vibración real del banco de rodamientos de la Case Western Reserve University (datos/cwru_12k_DE.npz):
rodamiento sano contra rodamiento con falla en la pista interior o exterior, a la carga que asigna el código.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S7"
CARPETA = "sesion_07_vibracion_y_monitoreo"
ALUMNO = os.path.join(AQUI, "S7_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S7_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S7_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S7_AC_CLASE_Colab_ALUMNO.ipynb"
RAMA = os.environ.get("DAQ_RAMA", "main")   # para probar una rama antes de aceptarla; los cuadernos publicados usan main
URL_NPZ = f"https://raw.githubusercontent.com/ggt13/DAQ_TSU/{RAMA}/" + CARPETA + "/datos/cwru_12k_DE.npz"

DATOS_S7 = f'URL_NPZ = "{URL_NPZ}"\n' + r'''
import io
import scipy.signal as ss

MAQUINAS = ["Motor de la bomba de agua helada, 30 kW", "Compresor de aire de tornillo, 37 kW",
            "Ventilador de la torre de enfriamiento, 18.5 kW", "Motor del chiller, 55 kW",
            "Ventilador de la manejadora de aire del cuarto limpio, 22 kW"]   # grupo 2 de ISO 10816-3, base rígida
ZONAS_ISO = [(1.4, "A · nueva o como nueva"), (2.8, "B · aceptable sin límite de tiempo"),
             (4.5, "C · insatisfactoria: planear la intervención"), (float("inf"), "D · puede causar daño")]
FS_B = 12000                                   # muestras por segundo de los registros de la CWRU
VENTANAS_B = 10                                # ventanas de 0.25 s en cada mitad del registro
MULT_CWRU = {"IR": 5.4152, "OR": 3.5848}       # múltiplos de la frecuencia de giro, rodamiento SKF 6205-2RS (CWRU)
NOMBRE_FALLA = {"IR": "pista interior", "OR": "pista exterior"}
COMBOS = [(f, c) for c in (0, 1, 3) for f in ("IR007", "OR007", "IR021", "OR021")]


def zona_iso(v):
    return next(z for lim, z in ZONAS_ISO if v <= lim)


def datos_s7(alumno):
    """Parte A: la máquina, su rodamiento, su vibración de hoy y su línea base."""
    rpm = int(round(parametro(alumno, "rpm", 1150, 3550, 0)))
    fr = rpm / 60
    n = asignar(alumno, [7, 8, 9, 10, 12], salto=1)
    D = parametro(alumno, "D_paso", 30, 60, 1)
    d = round(parametro(alumno, "relacion", 0.15, 0.30, 3) * D, 1)
    v_obj = parametro(alumno, "v_obj", 0.6, 5.0, 2)
    a1 = round(v_obj * np.sqrt(2) * 2 * np.pi * fr / 1000, 3)        # amplitud pico a 1×, m/s²
    a2 = parametro(alumno, "a2", 0.3, 1.5, 2)                         # amplitud pico a la frecuencia del rodamiento
    a_rms = np.sqrt((a1 ** 2 + a2 ** 2) / 2)
    media = round(parametro(alumno, "frac", 0.55, 0.95, 3) * a_rms, 3)
    s = round(parametro(alumno, "s_rel", 0.04, 0.10, 3) * media, 3)
    return dict(MAQUINA=asignar(alumno, MAQUINAS, salto=2), RPM=rpm, N_BOLAS=n, D_PASO=D, D_BOLA=d, A1=a1, A2=a2,
                MEDIA_BASE=media, S_BASE=s)


def clave_s7(alumno):
    d = datos_s7(alumno)
    fr = d["RPM"] / 60
    return {"bpfo_A": d["N_BOLAS"] / 2 * fr * (1 - d["D_BOLA"] / d["D_PASO"]),
            "a_rms_A": float(np.sqrt((d["A1"] ** 2 + d["A2"] ** 2) / 2)),
            "v_rms_A": d["A1"] / np.sqrt(2) / (2 * np.pi * fr) * 1000,
            "umbral_A": d["MEDIA_BASE"] + 3 * d["S_BASE"]}


def carga_cwru(alumno):
    """Los registros de la CWRU (≈ 2.4 MB): del repositorio o el archivo subido; si no, sintéticos marcados."""
    import urllib.request
    for origen in (URL_NPZ, "cwru_12k_DE.npz"):
        try:
            if origen.startswith("http"):
                with urllib.request.urlopen(origen, timeout=60) as r:
                    z = np.load(io.BytesIO(r.read()))
            else:
                z = np.load(origen)
            return {k: z[k] for k in z.files}, "CWRU Bearing Data Center, rodamiento del lado de acople"
        except Exception as e:
            print(f"⚠ No se pudo leer {origen}: {type(e).__name__}")
    print("⚠ Sube cwru_12k_DE.npz con el ícono de carpeta y vuelve a ejecutar. Mientras tanto se usan datos SINTÉTICOS.")
    g = alumno.rng("cwru")
    t = np.arange(5 * FS_B) / FS_B
    z = {}
    for f, c in COMBOS:
        rpm = 1797 - 25 * c
        fr = rpm / 60
        fd = MULT_CWRU[f[:2]] * fr
        golpes = (np.mod(t, 1 / fd) < 1 / FS_B).astype(float)
        reson = np.convolve(golpes, np.exp(-np.arange(200) / 25) * np.sin(2 * np.pi * 3200 * np.arange(200) / FS_B), "same")
        base = 0.05 * np.sin(2 * np.pi * fr * t) + g.normal(0, 0.06, t.size)
        z[f"{f}_{c}"] = (base + 1.5 * reson).astype(np.float32)
        z[f"normal_{c}"] = (0.05 * np.sin(2 * np.pi * fr * t) + g.normal(0, 0.06, t.size)).astype(np.float32)
        for k in (f"{f}_{c}", f"normal_{c}"):
            z["rpm_" + k], z["archivo_" + k] = np.array(rpm), np.array("sintético")
    return z, "SINTÉTICOS (sin el archivo de la CWRU)"


def rms_ventanas(x, n=VENTANAS_B):
    """RMS de n ventanas iguales del registro, sin la componente de directa de cada ventana."""
    x = np.asarray(x, float)
    v = x[: len(x) // n * n].reshape(n, -1)
    return np.sqrt(np.mean((v - v.mean(axis=1, keepdims=True)) ** 2, axis=1))


def mitades(x):
    """Primera mitad (línea base) y segunda mitad (prueba) del registro."""
    x = np.asarray(x, float)
    return x[: len(x) // 2], x[len(x) // 2:]


def factor_cresta(x):
    x = np.asarray(x, float) - np.mean(x)
    return float(np.max(np.abs(x)) / np.sqrt(np.mean(x ** 2)))


def velocidad_rms(a_pico, f):
    """Velocidad RMS en mm/s de una componente de aceleración pico a_pico (m/s²) a la frecuencia f (Hz)."""
    return a_pico / np.sqrt(2) / (2 * np.pi * f) * 1000


def frecuencias_rodamiento(rpm, n, d, D):
    fr = rpm / 60
    return {"BPFO (pista exterior)": n / 2 * fr * (1 - d / D), "BPFI (pista interior)": n / 2 * fr * (1 + d / D),
            "BSF (bola)": D / (2 * d) * fr * (1 - (d / D) ** 2), "FTF (jaula)": fr / 2 * (1 - d / D)}


def espectro(x, fs=FS_B):
    x = np.asarray(x, float) - np.mean(x)
    X = 2 * np.abs(np.fft.rfft(x * np.hanning(len(x)))) / np.sum(np.hanning(len(x)))
    return np.fft.rfftfreq(len(x), 1 / fs), X


def envolvente(x, fs=FS_B, banda=(2000, 5000)):
    """Espectro de la envolvente: filtro pasabanda donde resuenan los golpes, envolvente (Hilbert) y su espectro."""
    b, a = ss.butter(4, banda, btype="bandpass", fs=fs)
    e = np.abs(ss.hilbert(ss.filtfilt(b, a, np.asarray(x, float))))
    return espectro(e, fs)


def pico_cerca(f, E, f0, tol=0.1):
    """Frecuencia del pico más alto dentro de ±tol alrededor de f0."""
    k = (f > (1 - tol) * f0) & (f < (1 + tol) * f0)
    return float(f[k][np.argmax(E[k])])


def lee_phyphox(ruta):
    """CSV exportado de phyphox (Aceleración con o sin g). Devuelve fs, señal del eje que más vibra y su nombre.

    phyphox no muestrea a intervalo exacto: se remuestrea a intervalo fijo con la mediana de los intervalos.
    """
    import pandas as pd
    t = pd.read_csv(ruta, sep=None, engine="python")
    t = t.apply(pd.to_numeric, errors="coerce").dropna()
    tiempo = t.iloc[:, 0].to_numpy()
    ejes = [c for c in t.columns[1:] if "abs" not in c.lower()] or list(t.columns[1:])
    eje = max(ejes, key=lambda c: t[c].std())
    dt = float(np.median(np.diff(tiempo)))
    tt = np.arange(tiempo[0], tiempo[-1], dt)
    return 1 / dt, np.interp(tt, tiempo, t[eje].to_numpy()), eje


def picos(f, X, n=3, desde=3.0, separacion=2.0):
    """Las n líneas más altas del espectro a partir de `desde` Hz, separadas al menos `separacion` Hz."""
    orden = np.argsort(X)[::-1]
    elegidos = []
    for i in orden:
        if f[i] >= desde and all(abs(f[i] - g) > separacion for g in elegidos):
            elegidos.append(float(f[i]))
        if len(elegidos) == n:
            break
    return elegidos


def por_hz(f, E, hasta=400):
    """El espectro resumido a un valor por hertz (el máximo de cada intervalo de 1 Hz), de 1 a hasta Hz."""
    idx = np.floor(f).astype(int)
    return np.array([E[idx == k].max() for k in range(1, hasta + 1)])
'''

SOL = {
    "bpfo_A": "N_BOLAS / 2 * (RPM / 60) * (1 - D_BOLA / D_PASO)",
    "SUST_1": 'f"{N_BOLAS} / 2 × ({RPM} / 60) × (1 − {D_BOLA} / {D_PASO}) = {bpfo_A:.4g} Hz"',
    "PRED_1": '"si la pista exterior se daña aparecerá una línea en el espectro de la envolvente a esta frecuencia"',
    "a_rms_A": "np.sqrt((A1 ** 2 + A2 ** 2) / 2)",
    "SUST_2": 'f"√(({A1}² + {A2}²) / 2) = {a_rms_A:.4g} m/s²"',
    "PRED_2": '"el número que da el medidor de vibración resume todas las componentes y no dice de dónde viene"',
    "v_rms_A": "A1 / np.sqrt(2) / (2 * np.pi * RPM / 60) * 1000",
    "SUST_3": 'f"({A1} / √2) / (2π × {RPM} / 60) × 1000 = {v_rms_A:.4g} mm/s"',
    "PRED_3": '"con esta velocidad la máquina cae en una zona de la norma y eso dice si el desbalance ya es preocupante"',
    "umbral_A": "MEDIA_BASE + 3 * S_BASE",
    "SUST_4": 'f"{MEDIA_BASE} + 3 × {S_BASE} = {umbral_A:.4g} m/s²"',
    "PRED_4": '"si el RMS de hoy pasa este umbral la máquina ya no se comporta como en su línea base y hay que revisarla"',
    "CIERRE": ('f"Hoy el RMS es {a_rms_A:.3g} m/s² y el umbral {umbral_A:.3g} m/s², así que '
               '{\'la alarma sí dispara\' if a_rms_A > umbral_A else \'la alarma no dispara\'}; la velocidad total de '
               '{V_TOTAL:.3g} mm/s la pone en la zona {zona_iso(V_TOTAL)[0]} de la norma"'),
    "UMBRAL_B": "MEDIA_N + 3 * S_N",
    "F_DEF_PRED": "MULT * RPM_B / 60",
    "CONCLUSION_B": ('f"Predije la falla en {F_DEF_PRED:.4g} Hz y el espectro de la envolvente mostró el pico en '
                     '{F_DEF_OBT:.4g} Hz; el RMS sólo dice que algo cambió, la envolvente dice que es la {NOMBRE_FALLA[FALLA[:2]]}"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# S7 · Monitoreo basado en condición: vibración · ¿Qué le duele a la máquina?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Evaluar la condición de una máquina rotatoria con su vibración: el **valor RMS** dice **cuánto** vibra y se compara
con una **línea base** y con la norma; el **espectro** dice **de dónde** viene la vibración (desbalance a la
frecuencia de giro, rodamiento a sus frecuencias de falla). Es el mantenimiento **basado en condición**: se interviene
cuando la medición lo indica, no por calendario.

## La situación
Un ventilador, una bomba o un compresor de la planta empieza a sonar distinto. Antes de pararlo hay que saber si es
desbalance (se corrige en sitio) o un rodamiento dañado (hay que cambiarlo), y qué tan urgente es. En clase trabajas
con **tu** máquina: su velocidad, su rodamiento y su vibración. En la práctica analizas mediciones reales de un banco
de pruebas de rodamientos de la Case Western Reserve University (CWRU), sano contra dañado.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero): la frecuencia de falla de tu rodamiento, el RMS, la velocidad de vibración contra la norma y el umbral de alarma. En cada uno escribes tu resultado, la sustitución con tus números y su unidad, y lo que predice | El diagnóstico de tu máquina |
| **B · Práctica** | 80 min | Con vibración real del banco de la CWRU: umbral con la línea base, frecuencia de falla predicha y encontrada en el espectro de la envolvente | Gráficas firmadas, tu conclusión y el archivo `S7_<código>.csv` |
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
- **Seguridad:** el sensor se coloca y se retira con la máquina **detenida**, con el procedimiento de bloqueo y
  etiquetado de la planta; sólo sobre la carcasa o la caja del rodamiento, nunca cerca de partes que giran, y sin
  ropa, cables ni gafetes colgando. Las guardas se quedan puestas.
"""),
         cu.guia(),
         cu.herramientas(DATOS_S7)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** máquina. La **frecuencia de giro** es f_r = rpm / 60, en hertz (vueltas por segundo).
Un **desbalance** vibra a f_r (una vez por vuelta); un defecto en la **pista exterior** del rodamiento produce un
golpe cada vez que pasa una bola, a la frecuencia **BPFO** (*ball pass frequency, outer race*).

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
bpfo_A = 104.7
SUST_1 = "9 / 2 × (1750 / 60) × (1 − 7.9 / 39.0) = 104.7 Hz"
PRED_1 = "si la pista exterior se daña aparecerá una línea nueva a esa frecuencia en el espectro"
```
Para escribir **m/s²** basta «m/s2»; para la raíz, «√» o «raiz». **RPM** es la velocidad de **giro** de la flecha;
no la confundas con la velocidad de **vibración** del ejercicio 3.
"""),
          cu.code("""
globals().update(datos_s7(alumno))
print(f"Tu máquina · {MAQUINA}")
print(f"  Velocidad de giro: RPM = {RPM} rpm")
print(f"  Rodamiento: N_BOLAS = {N_BOLAS} bolas · diámetro de bola D_BOLA = {D_BOLA} mm · "
      f"diámetro primitivo D_PASO = {D_PASO} mm (ángulo de contacto 0°)")
print(f"  Vibración de hoy: a 1× (desbalance) A1 = {A1} m/s² pico · a la frecuencia BPFO del rodamiento A2 = {A2} m/s² pico")
print(f"  Línea base (10 mediciones cuando la máquina estaba sana): media del RMS MEDIA_BASE = {MEDIA_BASE} m/s² · "
      f"desviación estándar S_BASE = {S_BASE} m/s²")
"""),
          cu.md("""
### ★ Ejercicio 1 · La frecuencia de falla de tu rodamiento (3 pts)
**Para qué sirve:** es la «huella digital» de una pista exterior dañada; sin ella, una línea en el espectro no se
puede atribuir a nada.

**BPFO = (n / 2) · f_r · (1 − d / D)**, con n bolas, d el diámetro de bola, D el diámetro primitivo y f_r = rpm / 60.
Calcula `bpfo_A` en Hz.
"""),
          cu.ejercicio(h, 1, "bpfo_A", [("tu número de bolas", "N_BOLAS"), ("tu velocidad", "RPM"),
                                        ("tu diámetro de bola", "D_BOLA"), ("tu diámetro primitivo", "D_PASO")],
                       ["Hz", "hz", "HZ", "hertz", "Hertz"]),
          cu.md("""
### Ejercicio 2 · ¿Cuánto vibra en total? RMS (2 pts)
**Para qué sirve:** el RMS es el número que da un medidor de vibración y el que se vigila contra la línea base.

Una senoidal de amplitud pico A tiene RMS = A / √2. Si hay dos componentes de frecuencias distintas, sus potencias se
suman: **RMS = √((A1² + A2²) / 2)**. Calcula `a_rms_A` en m/s².
"""),
          cu.ejercicio(h, 2, "a_rms_A", [("tu A1", "A1"), ("tu A2", "A2")], ["m/s2", "m/s²", "m/s^2", "M/S2", "m/s/s"]),
          cu.md("""
### Ejercicio 3 · ¿Qué dice la norma? Velocidad de vibración (2 pts)
**Para qué sirve:** las normas de severidad (ISO 10816-3, hoy ISO 20816-3) se expresan en **velocidad** RMS, en mm/s.

Para una senoidal de frecuencia f, la velocidad es la aceleración dividida entre 2πf. Calcula la velocidad RMS del
desbalance: **v = (A1 / √2) / (2π · RPM / 60) × 1000**, en mm/s (el 1000 pasa de m/s a mm/s).

La norma juzga la velocidad RMS **total** (todas las componentes de 10 a 1000 Hz); después del ejercicio el cuaderno
le suma la del rodamiento. Referencia, máquinas de 15 a 300 kW en base rígida (grupo 2): zona A hasta 1.4 mm/s ·
B hasta 2.8 · C hasta 4.5 · D arriba. En base flexible los límites son 2.3, 4.5 y 7.1 mm/s.
"""),
          cu.ejercicio(h, 3, "v_rms_A", [("tu A1", "A1"), ("tu velocidad de giro", "RPM")], ["mm/s", "MM/S", "mm/seg"]),
          cu.md("""
### Ejercicio 4 · El umbral de alarma (2 pts)
**Para qué sirve:** cada máquina vibra distinto; el umbral se fija con **su** historia sana, no con un número de
catálogo.

Con la línea base: **umbral = media + 3 · s**. Si la máquina sigue sana, casi ninguna medición lo rebasa. Calcula
`umbral_A` en m/s².
"""),
          cu.ejercicio(h, 4, "umbral_A", [("tu media de la línea base", "MEDIA_BASE"),
                                          ("tu desviación de la línea base", "S_BASE")],
                       ["m/s2", "m/s²", "m/s^2", "M/S2", "m/s/s"]),
          cu.md("La gráfica arma la vibración de hoy con tus dos componentes: arriba, en el tiempo; abajo, su espectro "
                "(amplitud pico de cada componente), con la frecuencia de giro, su doble (2×, donde aparecería una "
                "desalineación) y la BPFO marcadas. Debajo, las demás frecuencias de tu rodamiento y el desplazamiento."),
          cu.code("""
if not 0 < bpfo_A < 1000:
    raise ValueError("Tu BPFO debe ser positiva y de unos cuantos cientos de Hz como máximo: revisa el ejercicio 1.")
FR_RO = frecuencias_rodamiento(RPM, N_BOLAS, D_BOLA, D_PASO)
BPFO_V = FR_RO["BPFO (pista exterior)"]              # la señal se arma con la BPFO verdadera, no con la tuya
fs_a = 20 * BPFO_V
t = np.arange(int(20 * fs_a)) / fs_a                 # 20 s: resolución de 0.05 Hz
x = A1 * np.sin(2 * np.pi * RPM / 60 * t) + A2 * np.sin(2 * np.pi * BPFO_V * t + 0.7) + alumno.rng("ruido").normal(0, 0.05, t.size)
f, X = espectro(x, fs_a)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6))
a1.plot(t[t < 0.2] * 1000, x[t < 0.2], color="#1F5FAD", lw=1)
a1.set_xlabel("tiempo (ms)"); a1.set_ylabel("aceleración (m/s²)")
titulo(a1, f"Vibración de hoy · RMS {np.sqrt((A1 ** 2 + A2 ** 2) / 2):.3g} m/s²", alumno)
a2.plot(f, X, color="#1F5FAD", lw=1); a2.set_xlim(0, 1.5 * max(BPFO_V, 2 * RPM / 60))
for fx, txt in ((RPM / 60, "1×: desbalance"), (2 * RPM / 60, "2×: desalineación"), (bpfo_A, "tu BPFO")):
    a2.axvline(fx, color="#D9822B", ls="--", lw=1); a2.text(fx, a2.get_ylim()[1] * 0.9, " " + txt, color="#D9822B", fontsize=9)
a2.set_xlabel("frecuencia (Hz)"); a2.set_ylabel("amplitud pico (m/s²)")
firma(fig, alumno); plt.tight_layout(rect=(0, 0.05, 1, 1)); plt.show()
V_TOTAL = float(np.sqrt(velocidad_rms(A1, RPM / 60) ** 2 + velocidad_rms(A2, BPFO_V) ** 2))
X_PP_UM = 2 * np.sqrt(2) * v_rms_A / (2 * np.pi * RPM / 60) * 1000
print("Frecuencias de tu rodamiento: " + " · ".join(f"{k} {v:.1f} Hz" for k, v in FR_RO.items()))
print(f"Desplazamiento pico a pico del desbalance: {X_PP_UM:.1f} µm (a baja frecuencia manda el desplazamiento; "
      "a alta, la aceleración)")
print(f"Velocidad RMS total (1× y rodamiento): {V_TOTAL:.3g} mm/s → zona {zona_iso(V_TOTAL)}")
print(f"Hoy: RMS {a_rms_A:.3g} m/s² · umbral {umbral_A:.3g} m/s²")
"""),
          cu.md("""
### Cierre (1 pt)
Con tu RMS de hoy y tu umbral, ¿dispara la alarma? ¿En qué zona de la norma queda tu velocidad **total** (impresa
arriba)? ¿Qué harías con la máquina? Al menos 20 palabras, con tus tres números.
"""),
          cu.code(h("CIERRE") + "\n\nrevisa_texto('Cierre', CIERRE, {'tu RMS de hoy': a_rms_A, 'tu umbral': umbral_A,\n"
                  "             'tu velocidad total': V_TOTAL})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** con vibración real, detectar con el RMS **que** algo cambió y encontrar en el espectro **qué** cambió.

El banco de la CWRU tiene un motor de 2 HP con un rodamiento SKF 6205 del lado del acople, medido con un
acelerómetro a 12 000 muestras por segundo. Se probó con rodamientos sanos y con un defecto de 0.18 o 0.53 mm (0.007 o
0.021 in) hecho a propósito en la pista interior o en la exterior. Cada alumno recibe, según su código, un tipo de
falla y una carga del motor; compara el rodamiento sano y el dañado a la misma carga. Las aceleraciones están en g
(1 g = 9.81 m/s²), como en el registro original. Cada registro dura 5 s a 12 000 muestras/s: el espectro distingue
frecuencias separadas 1/5 s = 0.2 Hz y llega hasta 6000 Hz (la mitad de la frecuencia de muestreo, sesión 2).

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos | 10 | Cargas los dos registros de 5 s y los miras en el tiempo |
| B2 · Línea base y umbral | 15 | Con el RMS del rodamiento sano calculas el umbral y ves si el dañado lo rebasa |
| B3 · Predicción | 10 | Calculas la frecuencia de falla que debe aparecer |
| B4 · Envolvente | 20 | El espectro normal no la muestra clara; el de la envolvente sí. Comparas predicha contra encontrada |
| B5 · Conclusión | 15 | Diagnóstico con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
if "Z" not in globals() or FUENTE.startswith("SINTÉTICOS"):
    Z, FUENTE = carga_cwru(alumno)
FALLA, CARGA = asignar(alumno, COMBOS)
X_N, X_F = Z[f"normal_{CARGA}"].astype(float), Z[f"{FALLA}_{CARGA}"].astype(float)
RPM_B = int(Z[f"rpm_{FALLA}_{CARGA}"])
MULT = MULT_CWRU[FALLA[:2]]
print(f"B1 · Fuente: {FUENTE}")
print(f"     Tu caso: falla en la {NOMBRE_FALLA[FALLA[:2]]} de {int(FALLA[2:]) / 1000:.3f} in · carga {CARGA} HP · "
      f"RPM_B = {RPM_B} rpm · archivos CWRU {Z['archivo_normal_' + str(CARGA)]} (sano) y {Z[f'archivo_{FALLA}_{CARGA}']} (dañado)")
t = np.arange(X_N.size) / FS_B
k = t < 0.1
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, sharey=True)
a1.plot(t[k] * 1000, X_N[k], color="#2E7D32", lw=0.8); a1.set_ylabel("g"); titulo(a1, f"Rodamiento sano · carga {CARGA} HP", alumno)
a2.plot(t[k] * 1000, X_F[k], color="#C62828", lw=0.8); a2.set_ylabel("g"); a2.set_xlabel("tiempo (ms)")
a2.set_title(f"Rodamiento con falla en la {NOMBRE_FALLA[FALLA[:2]]}")
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### B2 · Línea base y umbral
Con la **primera mitad** del registro sano (2.5 s, 10 ventanas de un cuarto de segundo) el cuaderno arma la línea base:
media `MEDIA_N` y desviación `S_N` del RMS. Calcula `UMBRAL_B` = media + 3·s, en g. Después el umbral se prueba con la
**segunda mitad** del sano (no se usó para fijarlo) y con el dañado. También se imprime el factor de cresta (pico / RMS)
de cada registro.
"""),
          cu.code("""
BASE_N = rms_ventanas(mitades(X_N)[0])
RMS_N, RMS_F = rms_ventanas(mitades(X_N)[1]), rms_ventanas(mitades(X_F)[1])
MEDIA_N, S_N = round(float(BASE_N.mean()), 4), round(float(BASE_N.std(ddof=1)), 4)
print("Línea base, RMS del sano en la 1.ª mitad (g):", "  ".join(f"{v:.4f}" for v in BASE_N))
print(f"MEDIA_N = {MEDIA_N} g · S_N = {S_N} g")
print(f"Factor de cresta · sano {factor_cresta(X_N):.1f} · dañado {factor_cresta(X_F):.1f} "
      "(una senoidal pura tiene 1.4; los golpes de un defecto lo suben, pero no siempre lo bastante para separar)")
"""),
          cu.code(h("UMBRAL_B", "✎ tu umbral, en g") + """

completa(UMBRAL_B, "tu umbral")
import matplotlib.ticker as mt
alarmas_f, alarmas_n = int(np.sum(RMS_F > UMBRAL_B)), int(np.sum(RMS_N > UMBRAL_B))
OTRA = asignar(alumno, [c for c in (0, 1, 3) if c != CARGA], salto=1)
alarmas_otra = int(np.sum(rms_ventanas(mitades(Z[f"normal_{OTRA}"])[1]) > UMBRAL_B))
fig, ax = plt.subplots()
ax.plot(range(1, 11), BASE_N, "o:", color="#9CCC9C", label="sano, línea base")
ax.plot(range(11, 21), RMS_N, "o-", color="#2E7D32", label="sano, prueba")
ax.plot(range(11, 21), RMS_F, "s-", color="#C62828", label="dañado, prueba")
ax.axhline(UMBRAL_B, color="#444", ls="--", label=f"umbral {UMBRAL_B:.4f} g")
ax.set_xlabel("ventana de 0.25 s"); ax.set_ylabel("RMS (g)"); ax.set_yscale("log")
ax.yaxis.set_major_formatter(mt.ScalarFormatter()); ax.yaxis.set_minor_formatter(mt.NullFormatter())
ax.legend(fontsize=8)
titulo(ax, "RMS contra el umbral", alumno)
firma(fig, alumno); plt.show()
print(f"Ventanas de prueba sobre el umbral · dañado: {alarmas_f} de 10 · sano: {alarmas_n} de 10 (falsas alarmas)")
print(f"El dañado vibra {RMS_F.mean() / RMS_N.mean():.1f} veces más que el sano (RMS)")
rms_otra = float(rms_ventanas(mitades(Z[f"normal_{OTRA}"])[1]).mean())
print(f"¿Y si cambia la carga? El rodamiento SANO a {OTRA} HP tiene un RMS de {rms_otra:.4f} g y rebasa tu umbral en "
      f"{alarmas_otra} de 10 ventanas. " + ("Más carga o más vibración de fondo da falsas alarmas" if rms_otra > MEDIA_N
      else "Con menos vibración de fondo el umbral queda lejos y una falla incipiente tardaría en dispararlo") +
      ": la línea base sólo vale para la condición de operación en que se midió.")
"""),
          cu.md("""
### B3 · Predicción de la frecuencia de falla
La CWRU publica para este rodamiento los múltiplos de la frecuencia de giro: pista interior **5.4152**, pista
exterior **3.5848**. Calcula la frecuencia de **tu** falla: `F_DEF_PRED` = múltiplo × RPM_B / 60, en Hz. Tu múltiplo
está impreso abajo.
"""),
          cu.code('print(f"Tu múltiplo: MULT = {MULT} ({NOMBRE_FALLA[FALLA[:2]]}) · RPM_B = {RPM_B} rpm")'),
          cu.code(h("F_DEF_PRED", "✎ tu frecuencia de falla predicha, en Hz") + """

completa(F_DEF_PRED, "tu frecuencia predicha")
print(f"Predicción: {F_DEF_PRED:.1f} Hz · frecuencia de giro: {RPM_B / 60:.2f} Hz")
"""),
          cu.md("""
### B4 · Espectro y espectro de la envolvente
Arriba, el espectro **normal** del rodamiento dañado: muchas líneas y la de la falla no destaca. Cada golpe de la bola
contra el defecto hace «sonar» la estructura a varios kilohertz; abajo, el cuaderno filtra esa zona (2 a 5 kHz), toma
la **envolvente** de los golpes y calcula su espectro. Ahí la falla aparece como una línea a su frecuencia y a sus
múltiplos. Las líneas verticales son **tu** predicción. El cuaderno busca el pico cerca de la frecuencia teórica, no
de la tuya: si te equivocaste, lo verás.

En una falla de **pista interior** el defecto gira con la flecha y entra y sale de la zona de carga una vez por
vuelta; por eso, junto a la línea de la falla aparecen **bandas laterales** separadas por la frecuencia de giro.
"""),
          cu.code("""
fE_N, EN = envolvente(X_N); fE_F, EF = envolvente(X_F)
F_DEF_OBT = pico_cerca(fE_F, EF, MULT * RPM_B / 60)
f_s, S_F = espectro(X_F)
RESULTADOS = {"bpfo_A": bpfo_A, "a_rms_A": a_rms_A, "v_rms_A": v_rms_A, "umbral_A": umbral_A,
              "rpm_B": RPM_B, "carga_hp": CARGA, "media_n": MEDIA_N, "s_n": S_N, "umbral_B": UMBRAL_B,
              "alarmas_danado": alarmas_f, "alarmas_sano": alarmas_n, "alarmas_otra_carga": alarmas_otra,
              "rms_sano": float(RMS_N.mean()), "rms_danado": float(RMS_F.mean()),
              "f_def_pred": F_DEF_PRED, "f_def_obt": F_DEF_OBT}
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.5))
a1.plot(f_s, S_F, color="#888", lw=0.8); a1.set_xlim(0, 500); a1.set_ylim(0, 1.1 * S_F[f_s < 500].max()); a1.set_ylabel("amplitud (g)")
a1.axvline(F_DEF_PRED, color="#D9822B", ls="--", lw=1)
titulo(a1, "Espectro normal del rodamiento dañado", alumno)
a2.plot(fE_F, EF, color="#C62828", lw=1, label="dañado")
a2.plot(fE_N, EN, color="#2E7D32", lw=1.2, label="sano")
for m in (1, 2, 3):
    a2.axvline(m * F_DEF_PRED, color="#D9822B", ls="--", lw=1, label="tu predicción y sus múltiplos" if m == 1 else None)
a2.set_xlim(0, 500); a2.set_xlabel("frecuencia (Hz)"); a2.set_ylabel("amplitud de la envolvente (g)"); a2.legend(fontsize=8)
a2.set_title(f"Espectro de la envolvente · pico encontrado en {F_DEF_OBT:.1f} Hz")
firma(fig, alumno, RESULTADOS); plt.tight_layout(rect=(0, 0.05, 1, 1)); plt.show()
print(f"Predicha: {F_DEF_PRED:.1f} Hz · encontrada: {F_DEF_OBT:.1f} Hz · diferencia {100 * (F_DEF_OBT - F_DEF_PRED) / F_DEF_PRED:+.1f} %")
"""),
          cu.md("""
### B5 · Conclusión
¿Qué te dijo el RMS y qué te dijo la envolvente? ¿Coincide la frecuencia que encontraste con la que predijiste, y qué
recomendarías para esta máquina? Al menos 25 palabras, con tus dos frecuencias.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'tu frecuencia predicha': F_DEF_PRED, 'la frecuencia encontrada': F_DEF_OBT}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S7_<código>.csv` con el espectro de la envolvente de 1 a 400 Hz (un valor por hertz). En tu hoja
de resultados: abre la pestaña **CSV** → **Archivo → Importar → Subir** → elige el archivo → **Reemplazar la hoja
actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
ruta = f"S7_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"frecuencia_Hz": np.arange(1, 401), "envolvente_sano": por_hz(fE_N, EN), "envolvente_danado": por_hz(fE_F, EF)},
             extra={"fuente": FUENTE, "caso": f"{FALLA} a {CARGA} HP", "maquina": MAQUINA})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
"""),
          cu.md("""
## Opcional · Tu ventilador con phyphox (no se califica)
Una medición propia con el acelerómetro del teléfono. El teléfono muestrea a unos 100 a 500 lecturas por segundo y
no a intervalo exacto: alcanza para ver la vibración **1×** del ventilador y la de **paso de aspas** (número de aspas
× 1×), pero no las frecuencias de un rodamiento ni la envolvente; para eso se necesitan los 12 000 lecturas por
segundo de la CWRU (sesión 2: la frecuencia de muestreo decide qué se puede ver).

**Seguridad:** coloca y retira el teléfono con el ventilador **apagado y desconectado**. Fíjalo con cinta a la base
o a la carcasa, nunca sobre la rejilla ni cerca de las aspas. Si alteras el balanceo (un clip en una aspa), hazlo
con el ventilador desconectado y la rejilla puesta.

1. En phyphox abre **Aceleración (sin g)**, deja el teléfono fijo, enciende el ventilador y registra 20 s.
2. **⋮ → Exportar datos → CSV (coma, punto decimal)**; súbelo aquí con el ícono de carpeta y escribe su nombre abajo.
3. Ejecuta. Repite con el ventilador en otra velocidad o con un clip en una aspa y compara la línea 1×.
"""),
          cu.code("""
ARCHIVO_PHYPHOX = ""   # opcional: el nombre del CSV que subiste, por ejemplo "Acceleration without g.csv"

import os
if not ARCHIVO_PHYPHOX or not os.path.exists(ARCHIVO_PHYPHOX):
    print("Sin archivo de phyphox: este bloque es opcional.")
else:
    fs_p, x_p, eje_p = lee_phyphox(ARCHIVO_PHYPHOX)
    f_p, X_p = espectro(x_p, fs_p)
    lineas = picos(f_p, X_p)
    fig, ax = plt.subplots()
    ax.plot(f_p, X_p, color="#1F5FAD", lw=1)
    for fx in lineas:
        ax.axvline(fx, color="#D9822B", ls="--", lw=1); ax.text(fx, ax.get_ylim()[1] * 0.9, f" {fx:.1f} Hz", color="#D9822B", fontsize=8)
    ax.set_xlim(0, fs_p / 2); ax.set_xlabel("frecuencia (Hz)"); ax.set_ylabel("amplitud pico (m/s²)")
    titulo(ax, f"Mi ventilador · eje {eje_p}", alumno)
    firma(fig, alumno); plt.show()
    print(f"Muestreo del teléfono: {fs_p:.0f} lecturas/s · se ve hasta {fs_p / 2:.0f} Hz · {x_p.size / fs_p:.0f} s de registro")
    print(f"RMS: {np.sqrt(np.mean((x_p - x_p.mean()) ** 2)):.3f} m/s²")
    print("Líneas más altas: " + " · ".join(f"{fx:.1f} Hz ({fx * 60:.0f} rpm)" for fx in lineas))
    print("La más baja suele ser la 1× (la velocidad del ventilador); si otra es un múltiplo entero, cuenta las aspas.")
""")]
    C += cu.cierre()
    if prof:
        C += [cu.md("""
---
# Sólo profesor · Clave del grupo y verificación de los CSV
1. Pega en `CODIGOS` la lista de códigos del grupo y ejecuta: la tabla da los resultados esperados de la parte A y el
   caso de la CWRU de cada alumno.
2. Sube los CSV entregados y ejecuta la última celda: rehace la parte B de cada alumno con los mismos registros.
   Tolerancia: 2 %.
"""),
              cu.code('''
import glob, pandas as pd
CODIGOS = """
217654321
219876543
""".split()
filas = []
for c in CODIGOS:
    a = identificar("Alumno Clave", c, SESION)
    d, k_ = datos_s7(a), clave_s7(a)
    fa, ca = asignar(a, COMBOS)
    filas.append({"codigo": c, "maquina": d["MAQUINA"], "RPM": d["RPM"], "caso_B": f"{fa} a {ca} HP",
                  **{x: round(float(v), 4) for x, v in k_.items()}, "zona": zona_iso(k_["v_rms_A"])[0]})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
def _difiere(x, ref):
    return abs(x - ref) > 0.02 * max(abs(ref), 1e-3)

for ruta in sorted(glob.glob("S7_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    a = identificar("Alumno Clave", meta["codigo"], SESION)
    k_ = clave_s7(a)
    malos = [x for x in k_ if x not in res or _difiere(res[x], k_[x])]
    fa, ca = asignar(a, COMBOS)
    if FUENTE.startswith("SINTÉTICOS") or str(meta.get("fuente", "")).startswith("SINTÉTICOS"):
        malos.append("fuente sintética: revisar la parte B a mano")
    elif meta.get("caso") != f"{fa} a {ca} HP":
        malos.append(f"caso ({meta.get('caso')} en el CSV, {fa} a {ca} HP asignado)")
    else:
        b0 = rms_ventanas(mitades(Z[f"normal_{ca}"])[0])
        rn, rf = rms_ventanas(mitades(Z[f"normal_{ca}"])[1]), rms_ventanas(mitades(Z[f"{fa}_{ca}"])[1])
        mu_, s_ = round(float(b0.mean()), 4), round(float(b0.std(ddof=1)), 4)
        u = mu_ + 3 * s_
        rpm_ = int(Z[f"rpm_{fa}_{ca}"])
        fp = MULT_CWRU[fa[:2]] * rpm_ / 60
        f_, E_ = envolvente(Z[f"{fa}_{ca}"])
        esperado = {"rpm_B": rpm_, "media_n": mu_, "s_n": s_, "umbral_B": u, "alarmas_danado": int(np.sum(rf > u)),
                    "alarmas_sano": int(np.sum(rn > u)), "f_def_pred": fp, "f_def_obt": pico_cerca(f_, E_, fp)}
        malos += [x for x, v in esperado.items() if x not in res or _difiere(res[x], v)]
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · {fa} a {ca} HP · "
          + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("bpfo_A", "★ Frecuencia de falla de tu rodamiento, BPFO (Hz)", "0.0"),
                    ("a_rms_A", "RMS de hoy de tu máquina (m/s²)", "0.000"),
                    ("v_rms_A", "Velocidad RMS del desbalance (mm/s)", "0.00"),
                    ("umbral_A", "Umbral de alarma de tu máquina (m/s²)", "0.000"),
                    ("rpm_B", "Velocidad del banco de la CWRU (rpm)", "0"),
                    ("umbral_B", "Umbral con la línea base del rodamiento sano (g)", "0.0000"),
                    ("alarmas_danado", "Ventanas del dañado sobre el umbral (de 10)", "0"),
                    ("alarmas_sano", "Ventanas de prueba del sano sobre el umbral: falsas alarmas (de 10)", "0"),
                    ("alarmas_otra_carga", "Ventanas del sano a otra carga sobre tu umbral (de 10)", "0"),
                    ("rms_sano", "RMS promedio del sano (g)", "0.0000"),
                    ("rms_danado", "RMS promedio del dañado (g)", "0.0000"),
                    ("f_def_pred", "Frecuencia de falla predicha (Hz)", "0.0"),
                    ("f_def_obt", "Frecuencia encontrada en la envolvente (Hz)", "0.0")],
        comparacion=("f_def_pred", "f_def_obt", "Diferencia, encontrada contra predicha (%)"),
        preguntas=["1. ¿Por qué el RMS basta para saber que algo cambió, pero no para saber qué pieza falla? ¿Qué "
                   "pasó con tu umbral cuando cambió la carga? Usa tu umbral y tus RMS.",
                   "2. ¿Qué pieza del rodamiento está dañada según la envolvente y qué recomendarías hacer con la "
                   "máquina? Usa tus frecuencias predicha y encontrada."],
        tabla={"encabezado_csv": "frecuencia_Hz", "x": ("A", "Frecuencia (Hz)"),
               "series": [("B", "Sano"), ("C", "Dañado")]},
        grafica={"titulo": "Espectro de la envolvente", "x": "Frecuencia (Hz)", "y": "Amplitud (g)", "tipo": "linea"},
        renglones=400,
        metadatos=(("Fuente de los datos", "fuente"), ("Caso de la CWRU", "caso"), ("Máquina (parte A)", "maquina")),
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
                          os.path.join(sys.argv[2], "S7_resuelto.ipynb"))
        print("  prueba:", ruta)
