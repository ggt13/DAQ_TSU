"""Sesión 3 · Calibración y ajuste de curvas. Genera:

    S3_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S3_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S3_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s3.py            -> los tres archivos
      python gen_s3.py --prueba D -> además, una versión resuelta en D para ejecutarla

Datos de la práctica: mediciones reales de la generación 2025 (Arduino, 10 bits, 5 V) de un potenciómetro rotatorio
(subida y bajada) y uno deslizable.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S3"
CARPETA = "sesion_03_calibracion_y_ajuste"
ALUMNO = os.path.join(AQUI, "S3_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S3_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S3_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S3_AC_CLASE_Colab_ALUMNO.ipynb"

DATOS_S3 = '''
# Mediciones reales de la generación 2025 (Arduino, 10 bits, 5 V)
GRADOS = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210,
                   220, 230, 240, 250, 260, 270, 280, 290])
SUBIDA = np.array([0.0, 0.0, 0.005, 0.22, 0.415, 0.606, 0.821, 1.007, 1.183, 1.393, 1.603, 1.808, 2.028, 2.278, 2.473,
                   2.669, 2.874, 3.079, 3.309, 3.524, 3.739, 3.93, 4.12, 4.301, 4.506, 4.663, 4.848, 5.0, 5.0, 5.0])
BAJADA = np.array([0, 0, 0.059, 0.244, 0.45, 0.65, 0.86, 1.017, 1.217, 1.403, 1.65, 1.818, 2.038, 2.258, 2.463, 2.654,
                   2.903, 3.113, 3.338, 3.529, 3.719, 3.935, 4.125, 4.326, 4.497, 4.687, 4.795, 5, 5, 5])
CM = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0])
V_DESL = np.array([0.0, 0.044, 0.225, 0.538, 1.408, 2.278, 2.947, 3.456, 3.978, 4.492, 4.814, 4.951, 5.0])
FUENTE = "Mediciones de la generación 2025 (Arduino, 10 bits, 5 V)"


def datos_s3(alumno):
    """Transmisor de presión con 0.5 V a 4.5 V nominales; puntos de calibración a 10, 30, 50, 70 y 90 % del alcance."""
    alcance = asignar(alumno, [6, 10, 16, 25, 40])
    g = parametro(alumno, "ganancia", 0.95, 1.05, 4)
    off = parametro(alumno, "offset", -0.08, 0.08, 3)
    curva = parametro(alumno, "curva", -0.06, 0.06, 3)
    x = np.round(alcance * np.array([0.1, 0.3, 0.5, 0.7, 0.9]), 2)
    f = x / alcance
    y = 0.5 + off + 4.0 * g * f + curva * 4 * f * (1 - f) + alumno.rng("ruido").normal(0, 0.004, x.size)
    v_nueva = parametro(alumno, "v_nueva", 1.2, 4.0, 3)
    return dict(ALCANCE=alcance, X_REF=x, Y_LECT=np.round(y, 3), V_NUEVA=v_nueva,
                V_LECT_B=parametro(alumno, "v_lect_b", 0.6, 4.3, 3))


def clave_s3(alumno):
    d = datos_s3(alumno)
    x, y = d["X_REF"], d["Y_LECT"]
    m = (y[-1] - y[0]) / (x[-1] - x[0])
    b = y[0] - m * x[0]
    return {"m_2p": m, "b_2p": b, "P_corr": (d["V_NUEVA"] - b) / m, "no_lin_V": float(abs(y[2] - (m * x[2] + b)))}


def ajuste(x, y, grado):
    c = np.polyfit(x, y, grado)
    yh = np.polyval(c, x)
    r2 = 1 - np.sum((y - yh) ** 2) / np.sum((y - np.mean(y)) ** 2)
    return c, yh, float(r2)


def revisa_rango(desde, hasta):
    """El rango útil no debe incluir puntos saturados (salida pegada a 0 V o a 5 V)."""
    if desde is None or hasta is None:
        raise ValueError("Escribe DESDE y HASTA, en grados.")
    k = (GRADOS >= desde) & (GRADOS <= hasta)
    sat = GRADOS[k & ((SUBIDA < 0.05) | (SUBIDA > 4.95))]
    faltan = []
    if k.sum() < 8:
        faltan.append("deja al menos 8 puntos para el ajuste")
    if len(sat):
        faltan.append("incluiste puntos saturados en " + ", ".join(f"{g}°" for g in sat))
    REGISTRO["Rango útil"] = not faltan
    if faltan:
        raise ValueError("Rango útil: " + "; ".join(faltan) + ".")
    print(f"✔ Rango útil de {desde}° a {hasta}°: {k.sum()} puntos, ninguno saturado.")
'''

SOL = {
    "m_2p": "(Y_LECT[-1] - Y_LECT[0]) / (X_REF[-1] - X_REF[0])",
    "SUST_1": 'f"({Y_LECT[-1]} − {Y_LECT[0]}) / ({X_REF[-1]:g} − {X_REF[0]:g}) = {m_2p:.5f} V/bar"',
    "PRED_1": '"cada bar de presión cambia la salida en esta cantidad y con eso se convierte cualquier lectura"',
    "b_2p": "Y_LECT[0] - m_2p * X_REF[0]",
    "SUST_2": 'f"{Y_LECT[0]} − {m_2p:.5f} × {X_REF[0]:g} = {b_2p:.4f} V"',
    "PRED_2": '"es la salida que daría el transmisor sin presión y no coincide exactamente con el medio volt nominal"',
    "P_corr": "(V_NUEVA - b_2p) / m_2p",
    "SUST_3": 'f"({V_NUEVA} − {b_2p:.4f}) / {m_2p:.5f} = {P_corr:.3f} bar"',
    "PRED_3": '"la lectura nueva se convierte con la recta de calibración y no con la regla de tres del catálogo"',
    "no_lin_V": "abs(Y_LECT[2] - (m_2p * X_REF[2] + b_2p))",
    "SUST_4": 'f"|{Y_LECT[2]} − ({m_2p:.5f} × {X_REF[2]:g} + {b_2p:.4f})| = {no_lin_V:.4f} V"',
    "PRED_4": '"es lo que se separa el punto central de la recta de dos puntos y muestra si el transmisor es lineal"',
    "CIERRE": ('f"Con dos puntos la pendiente es {m_2p:.5f} V/bar y por mínimos cuadrados {m_ls:.5f} V/bar; '
               'los mínimos cuadrados usan los cinco puntos y reparten mejor el error de cada uno"'),
    "DESDE": "30",
    "HASTA": "260",
    "ang_cal": "(V_LECT_B - b_rot) / m_rot",
    "GRADO_DESL": "3",
    "CONCLUSION_B": ('f"Mi lectura de {V_LECT_B} V corresponde a {ang_cal:.1f}° con la calibración y a {ang_regla:.1f}° '
                     'con la regla de tres; la calibración corrige el tramo muerto del inicio del potenciómetro"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# S3 · Calibración y ajuste de curvas · De la lectura al valor verdadero
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Obtener la **curva de calibración** de un sensor a partir de puntos medidos contra una referencia, usarla para
convertir una lectura en el valor físico, y decidir con los **residuos** si basta una recta o hace falta otro modelo.

## La situación
Un transmisor de presión nuevo se compara contra un calibrador patrón en cinco puntos. Su hoja de datos dice
«0.5 V a 4.5 V», pero cada pieza se desvía un poco: por eso se calibra. Cada alumno tiene su propio transmisor
(alcance, ganancia, offset y curvatura). En la práctica se usan mediciones reales de dos potenciómetros hechas por
la generación 2025 con Arduino.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero): calibración de dos puntos, conversión de una lectura y no linealidad. En cada uno escribes tu resultado, la sustitución con tus números y su unidad, y lo que predice | La recta de calibración de tu transmisor |
| **B · Práctica** | 80 min | Eliges el rango útil del potenciómetro rotatorio, ajustas la recta, conviertes tu lectura a ángulo y comparas recta contra polinomio en el deslizable | Gráficas firmadas, tu conclusión y el archivo `S3_<código>.csv` |
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
         cu.herramientas(DATOS_S3)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** transmisor: los cinco puntos de calibración (`X_REF`, presión del patrón en bar;
`Y_LECT`, salida del transmisor en V) y una lectura nueva `V_NUEVA` que hay que convertir. El primer punto es el
primer número de cada lista; el último, el último.

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
m_2p   = 0.2025
SUST_1 = "(4.12 − 0.88) / (18 − 2) = 0.2025 V/bar"
PRED_1 = "cada bar más de presión sube la salida unas dos décimas de volt en todo el alcance"
```
"""),
          cu.code("""
globals().update(datos_s3(alumno))
print(f"Tu transmisor · alcance 0 a {ALCANCE} bar · lectura nueva V_NUEVA = {V_NUEVA} V")
print("  X_REF (bar):", ", ".join(f"{x:g}" for x in X_REF))
print("  Y_LECT (V): ", ", ".join(f"{y:.3f}" for y in Y_LECT))
"""),
          cu.md("""
### ★ Ejercicio 1 · Pendiente de la calibración de dos puntos (3 pts)
**Para qué sirve:** es la sensibilidad real de **tu** pieza, no la del catálogo. Con ella se convierte cualquier lectura.

Con el primer y el último punto: **m = (y₂ − y₁) / (x₂ − x₁)**. Calcula `m_2p` en V/bar.
"""),
          cu.ejercicio(h, 1, "m_2p", [("tu primer voltaje", "Y_LECT[0]"), ("tu último voltaje", "Y_LECT[-1]"),
                                      ("tu primera presión", "X_REF[0]"), ("tu última presión", "X_REF[-1]")], ["V/bar"]),
          cu.md("""
### Ejercicio 2 · Ordenada al origen (2 pts)
**Para qué sirve:** es lo que saldría sin presión: el offset real de tu pieza.

La recta pasa por tu primer punto; despeja **b** de y = m·x + b. Calcula `b_2p` en V.
"""),
          cu.ejercicio(h, 2, "b_2p", [("tu primer voltaje", "Y_LECT[0]"), ("tu m", "m_2p")], ["V"]),
          cu.md("""
### Ejercicio 3 · De la lectura a la presión (2 pts)
**Para qué sirve:** es para lo que se calibra: convertir lo que marca el instrumento en el valor físico.

Despeja **x** de la recta para tu `V_NUEVA`. Calcula `P_corr` en bar.
"""),
          cu.ejercicio(h, 3, "P_corr", ["V_NUEVA"], ["bar"]),
          cu.md("""
### Ejercicio 4 · ¿Qué tan recta es? (2 pts)
**Para qué sirve:** si los puntos intermedios se separan mucho de la recta, una calibración de dos puntos no basta.

En el **punto central** (el tercero, 50 % del alcance), calcula qué voltaje da tu recta (m·x + b) y réstalo del
voltaje medido ahí. La **no linealidad** es esa diferencia sin signo. Resultado en V.
"""),
          cu.ejercicio(h, 4, "no_lin_V", [("tu voltaje central", "Y_LECT[2]"), ("tu presión central", "X_REF[2]")], ["V"]),
          cu.code("""
m_ls, b_ls = np.polyfit(X_REF, Y_LECT, 1)
xx = np.linspace(0, ALCANCE, 100)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
a1.plot(X_REF, Y_LECT, "o", label="puntos de calibración")
a1.plot(xx, m_2p * xx + b_2p, label="recta de dos puntos")
a1.plot(xx, m_ls * xx + b_ls, "--", label="mínimos cuadrados")
a1.set_xlabel("presión del patrón (bar)"); a1.set_ylabel("salida (V)"); a1.legend(fontsize=8)
titulo(a1, "Calibración", alumno)
a2.axhline(0, color="#444", lw=1); a2.vlines(X_REF, 0, Y_LECT - (m_2p * X_REF + b_2p), color="#C62828", lw=3)
a2.set_xlabel("presión (bar)"); a2.set_ylabel("residuo (V)"); a2.set_title("Residuos de la recta de dos puntos")
firma(fig, alumno); plt.tight_layout(rect=(0, 0.06, 1, 1)); plt.show()
print(f"Mínimos cuadrados con los cinco puntos: m_ls = {m_ls:.5f} V/bar · b_ls = {b_ls:.4f} V")
"""),
          cu.md("""
### Cierre (1 pt)
Compara tu pendiente de dos puntos con la de mínimos cuadrados (`m_ls`, impresa arriba). ¿Por qué no son iguales y
cuál usarías? Al menos 20 palabras, con las dos pendientes.
"""),
          cu.code(h("CIERRE") + "\n\nrevisa_texto('Cierre', CIERRE, {'tu pendiente de dos puntos': m_2p,\n"
                  "             'la pendiente de mínimos cuadrados': m_ls})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** calibrar con datos reales, elegir el rango útil y el modelo, y medir lo que se gana contra la regla de tres.

Mediciones de la generación 2025 con Arduino: un potenciómetro **rotatorio** medido de 0° a 290° en subida y bajada, y
uno **deslizable** de 0 a 6 cm.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Rango útil | 20 | Eliges desde qué ángulo y hasta cuál la salida no está saturada |
| B2 · Tu lectura | 20 | Ajustas la recta en tu rango y conviertes tu lectura a ángulo |
| B3 · ¿Recta o polinomio? | 20 | En el deslizable eliges el grado del polinomio mirando los residuos |
| B4 · Conclusión | 10 | Comparas calibración contra regla de tres, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
fig, ax = plt.subplots()
ax.plot(GRADOS, SUBIDA, "o-", ms=4, label="subida"); ax.plot(GRADOS, BAJADA, "s", ms=3, alpha=0.6, label="bajada")
ax.set_xlabel("ángulo (°)"); ax.set_ylabel("salida (V)"); ax.set_xticks(range(0, 291, 30)); ax.grid(alpha=0.3); ax.legend()
titulo(ax, "Potenciómetro rotatorio, generación 2025", alumno)
firma(fig, alumno); plt.show()
print(f"Tu lectura para convertir: V_LECT_B = {V_LECT_B} V")
"""),
          cu.md("""
### B1 · Rango útil
Mira la gráfica: en los extremos la salida se queda pegada en 0 V o en 5 V (**saturación**). Escribe en `DESDE` y
`HASTA` el primer y el último ángulo (múltiplos de 10) donde la salida **sí** cambia. La celda revisa que no
incluyas puntos saturados.
"""),
          cu.code(h("DESDE", "✎ ángulo inicial, en grados", vacio="None") + "\n" +
                  h("HASTA", "✎ ángulo final, en grados", vacio="None") + """

revisa_rango(DESDE, HASTA)
k = (GRADOS >= DESDE) & (GRADOS <= HASTA)
(m_rot, b_rot), yh, R2_rot = ajuste(GRADOS[k], SUBIDA[k], 1)
histeresis_V = float(np.max(np.abs(SUBIDA[k] - BAJADA[k])))
print(f"Recta en {DESDE}°–{HASTA}°: m = {m_rot:.5f} V/° · b = {b_rot:.4f} V · R² = {R2_rot:.5f}")
print(f"Histéresis máxima (subida contra bajada) en tu rango: {histeresis_V:.3f} V")
"""),
          cu.md("""
### B2 · Tu lectura en grados
Con la recta de tu rango (`m_rot`, `b_rot`), convierte tu `V_LECT_B` a ángulo: `ang_cal`. El cuaderno la compara con
la **regla de tres** que usaría alguien sin calibrar (5 V ↔ 290°).
"""),
          cu.code(h("ang_cal") + """

completa(ang_cal, "el ángulo de tu lectura")
ang_regla = V_LECT_B / 5 * 290
xx = np.linspace(DESDE, HASTA, 100)
fig, ax = plt.subplots()
ax.plot(GRADOS, SUBIDA, "o", color="#BBB", label="fuera de tu rango")
ax.plot(GRADOS[k], SUBIDA[k], "o", label="tu rango")
ax.plot(xx, m_rot * xx + b_rot, lw=2, label=f"recta, R² = {R2_rot:.4f}")
ax.axhline(V_LECT_B, ls=":", c="#444"); ax.plot(ang_cal, V_LECT_B, "*", ms=14, c="#D9822B", label=f"tu lectura: {ang_cal:.1f}°")
ax.set_xlabel("ángulo (°)"); ax.set_ylabel("salida (V)"); ax.legend(fontsize=8)
titulo(ax, "Calibración del rotatorio", alumno)
firma(fig, alumno); plt.show()
print(f"Calibración: {ang_cal:.1f}° · regla de tres: {ang_regla:.1f}° · diferencia {ang_regla - ang_cal:+.1f}°")
"""),
          cu.md("""
### B3 · ¿Recta o polinomio? (deslizable)
Prueba en `GRADO_DESL` los grados 1, 2, 3 y 4; ejecuta cada vez y mira **la forma de los residuos**, no sólo R². Deja
el grado que elegirías y explica por qué en tu conclusión.
"""),
          cu.code(h("GRADO_DESL", "✎ grado del polinomio, de 1 a 4", vacio="None") + """

completa(GRADO_DESL, "el grado del polinomio")
c_d, yh_d, R2_desl = ajuste(CM, V_DESL, int(GRADO_DESL))
RESULTADOS = {"m_2p": m_2p, "b_2p": b_2p, "P_corr": P_corr, "no_lin_V": no_lin_V, "desde": DESDE, "hasta": HASTA,
              "m_rot": m_rot, "b_rot": b_rot, "R2_rot": R2_rot, "v_lect_b": V_LECT_B, "ang_cal": float(ang_cal),
              "ang_regla": ang_regla, "grado_desl": int(GRADO_DESL), "R2_desl": R2_desl}
xx = np.linspace(0, 6, 200)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
a1.plot(CM, V_DESL, "o"); a1.plot(xx, np.polyval(c_d, xx), lw=2)
a1.set_xlabel("posición (cm)"); a1.set_ylabel("salida (V)"); titulo(a1, f"Deslizable, grado {int(GRADO_DESL)}", alumno)
a2.axhline(0, color="#444", lw=1); a2.vlines(CM, 0, V_DESL - yh_d, color="#C62828", lw=3)
a2.set_xlabel("posición (cm)"); a2.set_ylabel("residuo (V)"); a2.set_title(f"R² = {R2_desl:.4f}")
firma(fig, alumno, RESULTADOS); plt.tight_layout(rect=(0, 0.06, 1, 1)); plt.show()
"""),
          cu.md("""
### B4 · Conclusión
¿Cuánto cambia tu lectura con la calibración frente a la regla de tres, y por qué? ¿Qué grado elegiste para el
deslizable? Al menos 25 palabras, con tus dos ángulos.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'tu ángulo calibrado': ang_cal, 'tu ángulo por regla de tres': ang_regla}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S3_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
recta = np.where(k, m_rot * GRADOS + b_rot, np.nan)
ruta = f"S3_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"grados": GRADOS, "V_subida": SUBIDA, "V_recta": ["" if np.isnan(v) else v for v in recta]},
             extra={"fuente": FUENTE, "rango": f"{DESDE} a {HASTA} grados"})
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
2. Sube los CSV entregados y ejecuta la última celda. En la parte B el rango lo elige el alumno: la celda rehace el
   ajuste con **su** rango y comprueba que su recta y su ángulo sean consistentes.
"""),
              cu.code('''
import pandas as pd, glob
CODIGOS = """
217654321
219876543
""".split()
filas = []
for c in CODIGOS:
    a = identificar("Alumno Clave", c, SESION)
    d, k_ = datos_s3(a), clave_s3(a)
    filas.append({"codigo": c, "alcance_bar": d["ALCANCE"], "V_NUEVA": d["V_NUEVA"], "V_LECT_B": d["V_LECT_B"],
                  **{x: round(float(v), 5) for x, v in k_.items()}})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
for ruta in sorted(glob.glob("S3_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    a = identificar("Alumno Clave", meta["codigo"], SESION)
    k_ = clave_s3(a)
    if "desde" in res and "hasta" in res:
        kk = (GRADOS >= res["desde"]) & (GRADOS <= res["hasta"])
        (m, b), _, _ = ajuste(GRADOS[kk], SUBIDA[kk], 1)
        k_.update({"m_rot": m, "b_rot": b, "ang_cal": (datos_s3(a)["V_LECT_B"] - b) / m})
    malos = [x for x in k_ if x not in res or abs(res[x] - k_[x]) > 0.02 * max(abs(k_[x]), 1e-3)]
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · rango "
          f"{res.get('desde')}–{res.get('hasta')}° · grado {res.get('grado_desl')} · "
          + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("m_2p", "★ Pendiente de dos puntos (V/bar)", "0.00000"),
                    ("b_2p", "Ordenada al origen (V)", "0.0000"),
                    ("P_corr", "Presión de tu lectura nueva (bar)", "0.000"),
                    ("no_lin_V", "No linealidad (V)", "0.0000"),
                    ("desde", "Rango útil del rotatorio, desde (°)", "0"),
                    ("hasta", "Rango útil del rotatorio, hasta (°)", "0"),
                    ("m_rot", "Pendiente del rotatorio (V/°)", "0.00000"),
                    ("R2_rot", "R² del rotatorio", "0.00000"),
                    ("ang_regla", "Tu lectura por regla de tres (°)", "0.0"),
                    ("ang_cal", "Tu lectura con la calibración (°)", "0.0"),
                    ("grado_desl", "Grado elegido para el deslizable", "0"),
                    ("R2_desl", "R² del deslizable", "0.0000")],
        comparacion=("ang_cal", "ang_regla", "Diferencia, regla de tres contra calibración (%)"),
        preguntas=["1. ¿Por qué la regla de tres da un ángulo distinto del calibrado? Usa tus números y la gráfica.",
                   "2. ¿Qué grado elegiste para el deslizable y qué viste en los residuos para decidirlo?"],
        tabla={"encabezado_csv": "grados", "x": ("A", "Ángulo (°)"),
               "series": [("B", "Medido"), ("C", "Recta")]},
        grafica={"titulo": "Calibración del potenciómetro rotatorio", "x": "Ángulo (°)", "y": "Salida (V)",
                 "tipo": "dispersion"},
        renglones=30,
        metadatos=(("Fuente de los datos", "fuente"), ("Rango útil", "rango")),
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
                          os.path.join(sys.argv[2], "S3_resuelto.ipynb"))
        print("  prueba:", ruta)
