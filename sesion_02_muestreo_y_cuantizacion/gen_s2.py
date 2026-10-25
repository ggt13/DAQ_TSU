"""Sesión 2 · Muestreo, cuantización y registro. Genera:

    S2_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S2_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S2_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s2.py            -> los tres archivos
      python gen_s2.py --prueba D -> además, una versión resuelta en D para ejecutarla
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S2"
CARPETA = "sesion_02_muestreo_y_cuantizacion"
ALUMNO = os.path.join(AQUI, "S2_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S2_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S2_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S2_AC_CLASE_Colab_ALUMNO.ipynb"

# Datos de la sesión: una sola definición, que usan el cuaderno del alumno y la clave del profesor
DATOS_S2 = '''
MEMORIA = 32000              # lecturas del Elitech RC-5
DT_MIN_RC5_S = 10            # intervalo mínimo del RC-5, en segundos
CAMPANA_DIAS = 7
ESCENARIOS = [  # lugar, variable, fenómeno más rápido, periodo base (s)
    ("Almacén de componentes sensibles a humedad", "HR", "ciclo del aire acondicionado", 900),
    ("Refrigerador de pasta de soldadura", "T", "ciclo del compresor", 1200),
    ("Cuarto de servidores", "T", "ciclo del aire acondicionado", 480),
    ("Línea SMT, ambiente", "T", "cambio de turno", 28800),
    ("Oficina con ventana al poniente", "T", "ciclo día–noche", 86400),
    ("Bodega de producto terminado", "HR", "ciclo día–noche", 86400),
    ("Área de empaque junto a la puerta de andén", "T", "apertura de la puerta", 300),
    ("Cámara de prueba de humedad con control on-off", "HR", "ciclo del control", 90),
    ("Gabinete de control con ventilador por termostato", "T", "encendido del ventilador", 100),
    ("Almacén de reactivos con extractor temporizado", "T", "ciclo del extractor", 1800),
]
RANGOS = {"T": (-30.0, 70.0, "°C"), "HR": (0.0, 100.0, "%")}


def datos_s2(alumno):
    """Los datos personales de la sesión 2."""
    lugar, variable, fenomeno, p_base = asignar(alumno, ESCENARIOS)
    d = dict(LUGAR=lugar, VARIABLE=variable, FENOMENO=fenomeno)
    d["P_S"] = int(round(p_base * parametro(alumno, "factor_P", 0.8, 1.25, 3)))
    d["DT_MAL_S"] = int(round(d["P_S"] * parametro(alumno, "mal", 0.55, 0.9, 3)))
    lo, hi, unidad = RANGOS[variable]
    d.update(R_MIN=lo, R_MAX=hi, RANGO=hi - lo, UNIDAD=unidad)
    d["N_BITS"] = asignar(alumno, [8, 10, 12], salto=2)
    d["DT_B_H"] = asignar(alumno, [20, 21, 27, 28, 30, 32], salto=3)
    return d


def clave_s2(alumno):
    """Resultados esperados de la parte A y de la predicción de la parte B."""
    d = datos_s2(alumno)
    f, fs = 1 / d["P_S"], 1 / d["DT_MAL_S"]
    fb, fsb = 1 / 24, 1 / d["DT_B_H"]
    return {
        "dt_max_s": d["P_S"] / 2,
        "T_aparente_s": 1 / abs(f - round(f / fs) * fs),
        "error_cuant": d["RANGO"] / 2 ** d["N_BITS"] / 2,
        "dias_memoria": MEMORIA * (d["P_S"] / 10) / 86400,
        "T_aparente_pred_h": 1 / abs(fb - round(fb / fsb) * fsb),
    }


def revisa_intervalo(dt, P_S):
    """Revisión del intervalo que el alumno elige para su campaña: cumple las tres reglas o dice cuál falla."""
    if dt is None:
        raise ValueError("Escribe el intervalo que programarías, en segundos.")
    faltan = []
    if dt < DT_MIN_RC5_S:
        faltan.append(f"el RC-5 no registra más rápido que cada {DT_MIN_RC5_S} s")
    if dt > P_S / 2:
        faltan.append("con ese intervalo hay aliasing: revisa el ejercicio 1")
    if MEMORIA * dt < CAMPANA_DIAS * 86400:
        faltan.append(f"la memoria se llena antes de {CAMPANA_DIAS} días: revisa el ejercicio 4")
    REGISTRO["Intervalo de la campaña"] = not faltan
    if faltan:
        raise ValueError("Intervalo de la campaña: " + "; ".join(faltan) + ".")
    print(f"✔ Intervalo de la campaña: {dt:g} s cumple las tres reglas.")


def periodo_dominante(t_h, y, minimo_h, maximo_h):
    """Periodo de la componente más fuerte de una serie muestreada a intervalo fijo (FFT con relleno de ceros)."""
    y = np.asarray(y, float)
    y = y - np.polyval(np.polyfit(t_h, y, 1), t_h)
    dt = t_h[1] - t_h[0]
    n = 16 * len(y)
    F = np.abs(np.fft.rfft(y, n))
    fr = np.fft.rfftfreq(n, dt)
    ok = (fr > 1 / maximo_h) & (fr < 1 / minimo_h)
    return 1 / fr[ok][np.argmax(F[ok])]
'''

SOL = {
    "dt_max_s": "P_S / 2",
    "SUST_1": 'f"{P_S} s / 2 = {dt_max_s:g} s"',
    "PRED_1": '"si el registrador guarda más espaciado que este intervalo el ciclo de mi escenario aparece falso o desaparece"',
    "T_aparente_s": "1 / abs(1 / P_S - 1 / DT_MAL_S)",
    "SUST_2": 'f"1 / |1/{P_S} − 1/{DT_MAL_S}| = {T_aparente_s:.1f} s"',
    "PRED_2": '"el registro mal hecho muestra un ciclo mucho más lento que el real y nadie lo notaría sin la teoría"',
    "error_cuant": "RANGO / 2 ** N_BITS / 2",
    "SUST_3": 'f"{RANGO:g} / 2**{N_BITS} / 2 = {error_cuant:.4g} {UNIDAD}"',
    "PRED_3": '"ninguna lectura puede alejarse del valor real más que medio escalón de mi convertidor por el redondeo"',
    "dias_memoria": "MEMORIA * (P_S / 10) / 86400",
    "SUST_4": 'f"{MEMORIA} × {P_S / 10:g} s / 86400 = {dias_memoria:.4g} días"',
    "PRED_4": '"con diez lecturas por ciclo la memoria dura ese número de días y así sé si cabe la campaña de una semana"',
    "INTERVALO_CAMPANA_S": "max(DT_MIN_RC5_S, int(np.ceil(CAMPANA_DIAS * 86400 / MEMORIA)), min(int(P_S / 10), int(P_S / 2)))",
    "JUSTIFICACION": ('f"Programo {INTERVALO_CAMPANA_S} s porque no pasa de {dt_max_s:g} s, el máximo por Nyquist, '
                      'es mayor que el mínimo del RC-5 y la memoria alcanza los siete días de la campaña"'),
    "T_aparente_pred_h": "1 / abs(1 / 24 - 1 / DT_B_H)",
    "CICLOS_CONTADOS": "round(HORAS / T_aparente_pred_h)",
    "CONCLUSION_B": ('f"Predije un ciclo falso de {T_aparente_pred_h:.4g} h y en la gráfica conté uno de {T_aparente_obt_h:.4g} h; '
                     'el registro cada {DT_B_H} h no ve el ciclo diario real de 24 h sino uno mucho más lento"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r or prof)
    C = [cu.md(f"""
# S2 · Muestreo, cuantización y registro · ¿Cada cuánto registrar sin que el registro mienta?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Elegir el **intervalo de registro** y estimar el **error de cuantización** de un registrador para un proceso de planta,
y comprobar con datos reales cómo un intervalo mal elegido inventa un ciclo que no existe (**aliasing**).

## La situación
Vas a dejar un registrador Elitech RC-5 siete días en un lugar de la planta. Cada alumno tiene un escenario distinto
(almacén, refrigerador, cuarto de servidores…), con su propio fenómeno más rápido y su periodo. Antes de programar el
registrador hay que contestar: ¿cada cuánto como máximo?, ¿qué pasa si me equivoco?, ¿qué tan fino mide? y ¿alcanza
la memoria?

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero) sobre **tu** escenario. En cada uno escribes la expresión en Python, la sustitución con tus números y su unidad, y lo que predice. Al final eliges el intervalo de tu campaña | Tus resultados, tus predicciones y el intervalo que programarás en el RC-5 |
| **B · Práctica** | 80 min | Tomas 60 días de temperatura real de Guadalajara, la registras con un intervalo demasiado largo y mides el ciclo falso que aparece | Gráficas firmadas, tu conclusión y el archivo `S2_<código>.csv` |
| **Hoja de resultados** | en la práctica | Importas el CSV en tu hoja de cálculo de Google y contestas las preguntas | El reporte que entregas |

## Qué entregas y cómo se califica
1. **Este cuaderno**, al terminar la sesión, con todo ejecutado. ★ 3 pts · ejercicios 2, 3 y 4, 2 pts cada uno ·
   cierre (intervalo de la campaña) 1 pt. Se califica que el resultado sea correcto para **tus** datos y que la
   sustitución y la predicción sean tuyas.
2. **La hoja de resultados** con el reporte, en 7 días naturales.
3. **Tu ficha de campaña** (al final del cuaderno), que sirve para elegir las tres campañas del grupo.

## Reglas
- **Archivo → Guardar una copia en Drive** antes de empezar; trabaja en tu copia.
- Completa sólo lo marcado con ✎. Ninguna celda avanza si falta algo: el mensaje dice qué.
- La revisión automática dice si el ejercicio está **completo**, no si está **bien**; eso lo califica el profesor.
- Si usas un asistente de IA, dilo en tu reporte. Las sustituciones y las respuestas llevan **tus** números.
"""),
         cu.herramientas(DATOS_S2)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** escenario.

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
dt_max_s = P_S / 2
SUST_1   = "600 s / 2 = 300 s"
PRED_1   = "si registro más espaciado que cinco minutos el ciclo del horno aparecerá falso en la gráfica"
```
"""),
          cu.code("""
globals().update(datos_s2(alumno))
print(f"Tu escenario · {LUGAR}")
print(f"  Variable: {VARIABLE} · fenómeno más rápido: {FENOMENO} · periodo P_S = {P_S} s ({P_S / 60:.1f} min)")
print(f"  Registrador: rango de {R_MIN:g} a {R_MAX:g} {UNIDAD} (RANGO = {RANGO:g} {UNIDAD}) · convertidor de N_BITS = {N_BITS} bits")
print(f"  Memoria: MEMORIA = {MEMORIA} lecturas · intervalo mal elegido para el ejercicio 2: DT_MAL_S = {DT_MAL_S} s")
"""),
          cu.md("""
### ★ Ejercicio 1 · ¿Cada cuánto como máximo? (3 pts)
**Para qué sirve:** es la regla que separa un registro útil de uno que miente. Si el registrador guarda más espaciado
que esto, el ciclo del proceso desaparece o aparece falso.

Criterio de Nyquist: **al menos dos lecturas por periodo**, es decir, **Δt_max = P / 2**. Calcula `dt_max_s` en segundos.
"""),
          cu.ejercicio(h, 1, "dt_max_s", ["P_S"], ["s"]),
          cu.md("""
### Ejercicio 2 · ¿Qué ciclo falso muestra un registro mal hecho? (2 pts)
**Para qué sirve:** reconocer el aliasing en un registro real: un ciclo lento que no existe y que lleva a decisiones
de mantenimiento equivocadas.

Si registras cada `DT_MAL_S` segundos (más que P/2), la frecuencia que aparece es la **diferencia** entre la frecuencia
real (1/P) y la del registro (1/Δt). El periodo aparente es el inverso de esa diferencia, en valor absoluto. Usa
`abs(...)` en Python. Resultado en segundos.
"""),
          cu.ejercicio(h, 2, "T_aparente_s", ["P_S", "DT_MAL_S"], ["s"]),
          cu.md("La gráfica muestra tu fenómeno (azul), las lecturas del registro mal hecho (puntos) y el ciclo que esas lecturas dibujan (línea discontinua): ese ciclo no existe. Si tu resultado del ejercicio 2 es correcto, la línea discontinua pasa por todos los puntos."),
          cu.code("""
t = np.linspace(0, 3 * T_aparente_s, 3000)
ts = np.arange(0, 3 * T_aparente_s, DT_MAL_S)
fig, ax = plt.subplots()
ax.plot(t / 60, np.sin(2 * np.pi * t / P_S), color="#9DB7D5", lw=1, label=f"{FENOMENO}, P = {P_S} s")
ax.plot(t / 60, -np.sin(2 * np.pi * t / T_aparente_s), "--", color="#D9822B", lw=1.5,
        label=f"ciclo falso que ve el registro, {T_aparente_s:.0f} s")
ax.plot(ts / 60, np.sin(2 * np.pi * ts / P_S), "o", color="#D9822B", ms=6, label=f"lecturas cada {DT_MAL_S} s")
ax.set_xlabel("tiempo (min)"); ax.set_yticks([]); ax.set_ylim(-1.15, 1.9)
ax.legend(loc="upper center", ncol=3, fontsize=8, frameon=False)
titulo(ax, "Un registro que miente", alumno)
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### Ejercicio 3 · ¿Qué tan fino mide? (2 pts)
**Para qué sirve:** es el error que agrega el registrador aunque el sensor fuera perfecto.

El convertidor divide el `RANGO` en 2ᴺ escalones y cada lectura se redondea al escalón más cercano. Calcula el
**error máximo de cuantización** (lo más lejos que puede quedar una lectura del valor real), en las unidades de tu
variable (`UNIDAD`).
"""),
          cu.ejercicio(h, 3, "error_cuant", ["RANGO", "N_BITS"], "[UNIDAD]"),
          cu.md("""
### Ejercicio 4 · ¿Alcanza la memoria? (2 pts)
**Para qué sirve:** decide si la campaña cabe completa o hay que ir a descargar a la mitad.

Un intervalo cómodo es **diez lecturas por ciclo** (Δt = P/10). Con ese intervalo, ¿cuántos **días** tarda en llenarse
la memoria de `MEMORIA` lecturas? (un día tiene 86 400 s)
"""),
          cu.ejercicio(h, 4, "dias_memoria", ["MEMORIA", "P_S / 10"], ["día"]),
          cu.md(f"""
### Cierre · El intervalo de tu campaña (1 pt)
Elige el intervalo, en segundos, que programarás en el RC-5 para registrar tu escenario **7 días**. Debe cumplir tres
reglas: no menor que {10} s (lo más rápido del RC-5), no mayor que tu `dt_max_s`, y que la memoria alcance los 7 días.
Después justifica tu elección con tus números (al menos 20 palabras).
"""),
          cu.code(h("INTERVALO_CAMPANA_S", "✎ el intervalo en segundos", vacio="None") + "\n" +
                  h("JUSTIFICACION") + "\n\n"
                  "revisa_intervalo(INTERVALO_CAMPANA_S, P_S)\n"
                  "revisa_texto('Justificación', JUSTIFICACION, {'el intervalo que elegiste': INTERVALO_CAMPANA_S,\n"
                  "             'tu intervalo máximo por Nyquist': dt_max_s})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** ver el aliasing en datos reales y comprobar que la fórmula del ejercicio 2 lo predice.

La temperatura de Guadalajara tiene un ciclo de **24 h** (día y noche). Vas a registrarla cada `DT_B_H` horas, más de
12 h, así que el registro miente. Los datos son 60 días reales, hora por hora
([Open-Meteo](https://open-meteo.com/), licencia CC BY 4.0); las fechas dependen de tu código.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos | 10 | Descargas los 60 días |
| B2 · Predicción | 15 | Calculas el periodo del ciclo falso que debe aparecer |
| B3 · Registro y conteo | 25 | Registras cada `DT_B_H` h, cuentas los ciclos falsos en la gráfica y calculas el periodo obtenido |
| B4 · Conclusión | 20 | Comparas predicho contra obtenido, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
import json, urllib.request, datetime as dt
inicio = dt.date(2025, 1, 6) + dt.timedelta(weeks=int(alumno.codigo) % 40)
fin = inicio + dt.timedelta(days=59)
url = ("https://archive-api.open-meteo.com/v1/archive?latitude=20.67&longitude=-103.35"
       f"&start_date={inicio}&end_date={fin}&hourly=temperature_2m&timezone=America%2FMexico_City")
try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        T_hora = np.array(json.load(resp)["hourly"]["temperature_2m"], dtype=float)
    FUENTE = "Open-Meteo (ERA5), Guadalajara"
except Exception as e:
    print("⚠ No se pudo descargar de Open-Meteo:", type(e).__name__, e)
    print("⚠ Se usan datos SINTÉTICOS. Vuelve a ejecutar esta celda con internet antes de entregar.")
    hh = np.arange(60 * 24)
    T_hora = (21 + 7 * np.sin(2 * np.pi * (hh - 9) / 24) + 2 * np.sin(2 * np.pi * hh / (24 * 9))
              + alumno.rng("ruido").normal(0, 0.7, hh.size))
    FUENTE = "SINTÉTICOS (sin conexión)"
HORAS = len(T_hora)
print(f"B1 · Del {inicio} al {fin} · {HORAS} lecturas horarias · fuente: {FUENTE}")
print(f"     Tu intervalo de registro para la práctica: DT_B_H = {DT_B_H} h")
"""),
          cu.md("""
### B2 · Predicción
Con la fórmula del ejercicio 2, ahora en horas: periodo real 24 h, registro cada `DT_B_H` h. ¿De cuántas horas será
el ciclo falso?
"""),
          cu.code(h("T_aparente_pred_h") + "\n\ncompleta(T_aparente_pred_h, 'la predicción del ciclo falso')\n"
                  "print(f'Predicción: un ciclo falso de {T_aparente_pred_h:.1f} h ({T_aparente_pred_h / 24:.1f} días)')"),
          cu.md("""
### B3 · Registro y conteo
La celda registra la temperatura cada `DT_B_H` horas y dibuja las dos series. **Cuenta en la gráfica de abajo cuántos
ciclos completos del registro (de máximo a máximo) caben en los 60 días** y escríbelo en `CICLOS_CONTADOS`.
El periodo obtenido es `HORAS / CICLOS_CONTADOS`.
"""),
          cu.code("""
inicio_h = int(alumno.codigo) % DT_B_H
t_reg = np.arange(inicio_h, HORAS, DT_B_H)
T_reg = T_hora[t_reg]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
a1.plot(np.arange(HORAS) / 24, T_hora, color="#9DB7D5", lw=0.8)
a1.set_ylabel("T (°C)"); titulo(a1, "Temperatura real, hora por hora", alumno)
a2.plot(t_reg / 24, T_reg, "-o", color="#D9822B", ms=3)
a2.set_ylabel("T (°C)"); a2.set_xlabel("día"); a2.set_xticks(range(0, 61, 5)); a2.grid(alpha=0.3)
a2.set_title(f"Registrada cada {DT_B_H} h: cuenta los ciclos")
firma(fig, alumno); plt.show()
"""),
          cu.code(h("CICLOS_CONTADOS", "✎ cuántos ciclos completos contaste", vacio="None") + """

completa(CICLOS_CONTADOS, "el número de ciclos que contaste")
T_aparente_obt_h = HORAS / CICLOS_CONTADOS
T_fft_h = periodo_dominante(t_reg, T_reg, 2 * DT_B_H, HORAS / 2)
RESULTADOS = {"dt_max_s": dt_max_s, "T_aparente_s": T_aparente_s, "error_cuant": error_cuant,
              "dias_memoria": dias_memoria, "intervalo_campana_s": INTERVALO_CAMPANA_S, "DT_B_h": DT_B_H,
              "T_aparente_pred_h": T_aparente_pred_h, "T_aparente_obt_h": T_aparente_obt_h}
print(f"Periodo obtenido por conteo: {T_aparente_obt_h:.1f} h · predicho: {T_aparente_pred_h:.1f} h")
print(f"(El cuaderno lo estima también con la transformada de Fourier: {T_fft_h:.1f} h)")
"""),
          cu.md("""
### B4 · Conclusión
¿El ciclo falso que contaste coincide con el que predijiste? ¿Qué le dirías a quien programó el registro cada
`DT_B_H` h? Al menos 25 palabras, con tus dos valores.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'el periodo predicho': T_aparente_pred_h, 'el periodo obtenido': T_aparente_obt_h}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S2_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
ruta = f"S2_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"dia": t_reg / 24, "T_registrada_C": T_reg},
             extra={"fuente": FUENTE, "periodo": f"{inicio} a {fin}", "escenario": LUGAR})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
"""),
          cu.md(f"""
## Siguiente paso · Las campañas de 7 días
El grupo tiene **tres** registradores RC-5, así que se harán tres campañas. Con las fichas de todos, el profesor elige
tres lugares de la planta y, para cada uno, el intervalo propuesto que mejor cumple las tres reglas.
1. Copia tu ficha de campaña (celda de abajo) en tu hoja de resultados, en la pregunta 2.
2. Quienes coloquen un registrador lo programan en ElitechLog con el intervalo elegido, toman una foto del
   registrador colocado con una tarjeta con su nombre a la vista y no lo mueven en 7 días.
3. Los tres archivos se comparten con todo el grupo: los usaremos en la sesión 5.
"""),
          cu.code('print(f"Ficha de campaña · {alumno.nombre} · {alumno.codigo} · {LUGAR} · {VARIABLE} · '
                  'intervalo {INTERVALO_CAMPANA_S} s · {CAMPANA_DIAS} días · {MEMORIA * INTERVALO_CAMPANA_S / 86400:.1f} días de memoria")')]
    C += cu.cierre()
    if prof:
        C += [cu.md("""
---
# Sólo profesor · Clave del grupo y verificación de los CSV
1. Pega en `CODIGOS` la lista de códigos del grupo (uno por renglón) y ejecuta: la tabla da los resultados esperados
   de cada alumno. Tolerancia sugerida: 2 % (redondeo de quien escribe 3 o 4 cifras).
2. Sube a esta sesión de Colab los CSV entregados (ícono de carpeta) y ejecuta la última celda: dice si la huella de
   cada uno es válida y compara sus resultados con la clave.
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
    d, k = datos_s2(a), clave_s2(a)
    filas.append({"codigo": c, "escenario": d["LUGAR"], "P_S": d["P_S"], "DT_MAL_S": d["DT_MAL_S"],
                  "N_BITS": d["N_BITS"], "DT_B_H": d["DT_B_H"], **{x: round(v, 4) for x, v in k.items()}})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
for ruta in sorted(glob.glob("S2_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    k = clave_s2(identificar("Alumno Clave", meta["codigo"], SESION))
    malos = [x for x in k if x not in res or abs(res[x] - k[x]) > 0.02 * abs(k[x])]
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · "
          f"fuente {meta.get('fuente')} · " + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("dt_max_s", "★ Intervalo máximo por Nyquist (s)", "0.0"),
                    ("T_aparente_s", "Periodo del ciclo falso, ejercicio 2 (s)", "0.0"),
                    ("error_cuant", "Error máximo de cuantización (unidad de tu variable)", "0.0000"),
                    ("dias_memoria", "Días que dura la memoria con P/10", "0.0"),
                    ("intervalo_campana_s", "Intervalo de tu campaña (s)", "0"),
                    ("DT_B_h", "Intervalo de la práctica (h)", "0"),
                    ("T_aparente_pred_h", "Ciclo falso predicho (h)", "0.0"),
                    ("T_aparente_obt_h", "Ciclo falso obtenido por conteo (h)", "0.0")],
        comparacion=("T_aparente_pred_h", "T_aparente_obt_h", "Diferencia, obtenido contra predicho (%)"),
        preguntas=["1. ¿Por qué el registro muestra un ciclo de varios días si la temperatura cicla cada 24 h? Usa tus números.",
                   "2. ¿Qué intervalo programaste para tu campaña y cómo cumple las tres reglas (mínimo del RC-5, "
                   "Nyquist y memoria)?"],
        tabla={"encabezado_csv": "dia", "x": ("A", "Día"), "series": [("B", "Registrada")]},
        grafica={"titulo": "Temperatura registrada en la práctica", "x": "Día", "y": "Temperatura (°C)",
                 "tipo": "dispersion"},
        renglones=80,
        metadatos=(("Fuente de los datos", "fuente"), ("Periodo", "periodo"), ("Escenario", "escenario")),
        csv_ejemplo=csv_ejemplo)


if __name__ == "__main__":
    cu.guardar(celdas(), ALUMNO)
    cu.guardar(celdas(prof=True), PROF)
    generar_hoja()
    print("listo:", ALUMNO, PROF, HOJA, sep="\n  ")
    if len(sys.argv) == 3 and sys.argv[1] == "--prueba":
        ruta = cu.guardar(celdas(r=True, nombre="Alumno De Prueba", codigo="217654321"),
                          os.path.join(sys.argv[2], "S2_resuelto.ipynb"))
        print("  prueba:", ruta)
