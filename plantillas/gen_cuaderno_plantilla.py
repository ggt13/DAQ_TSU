"""Genera el cuaderno de muestra del curso DAQ 2027 (sesión 0 · plantilla).

Uso:
    python gen_cuaderno_plantilla.py                  -> S0_AC_CLASE_Colab_PLANTILLA.ipynb (con huecos ✎)
    python gen_cuaderno_plantilla.py --resuelto RUTA  -> versión resuelta para probarla (no se sube al repositorio)

Estructura que deben seguir los cuadernos de las ocho sesiones:
  1. Objetivo y en qué consiste el cuaderno (situación, qué se hace, qué se entrega, cómo se califica).
  2. Herramientas del curso (oculta) e identificación.
  3. Parte A · actividad en clase: cuatro ejercicios (★ primero). En cada uno el alumno ESCRIBE la expresión
     en Python, la sustitución con sus números y su unidad, y lo que predice para la práctica. Ninguna celda
     avanza si falta algo de eso.
  4. Parte B · práctica: datos reales asignados por código; el alumno completa el cálculo clave y escribe su
     conclusión con sus números; CSV firmado para la hoja de resultados.
  5. Cierre con el estado de cada ejercicio y la huella.
"""
import os
import sys

import nbformat as nbf

AQUI = os.path.dirname(os.path.abspath(__file__))
IDENTIDAD = os.path.join(AQUI, "..", "comun", "identidad.py")
SALIDA = os.path.join(AQUI, "S0_AC_CLASE_Colab_PLANTILLA.ipynb")
COLAB = ("https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/"
         "plantillas/S0_AC_CLASE_Colab_PLANTILLA.ipynb")

# Lo que escribe el alumno: variable -> solución (sólo para la versión resuelta de prueba)
SOLUCION = {
    "lsb_C": "RANGO_C / 2 ** N_BITS",
    "SUST_1": 'f"{RANGO_C:g} / 2**{N_BITS} = {lsb_C:.4f} °C"',
    "PRED_1": '"en la práctica la temperatura registrada sólo puede cambiar en escalones de un LSB, nunca en valores intermedios"',
    "error_max_C": "lsb_C / 2",
    "SUST_2": 'f"{lsb_C:.4f} / 2 = {error_max_C:.4f} °C"',
    "PRED_2": '"al cuantizar la temperatura real de la semana el error de cada lectura no debe pasar de este valor"',
    "duracion_dias": "MEMORIA * INTERVALO_S / 86400",
    "SUST_3": 'f"{MEMORIA} × {INTERVALO_S} s / 86400 = {duracion_dias:.2f} días"',
    "PRED_3": '"con este intervalo el registrador alcanza para una campaña de esa duración antes de llenar su memoria"',
    "intervalo_max_min": "PERIODO_MIN / 2",
    "SUST_4": 'f"{PERIODO_MIN:g} min / 2 = {intervalo_max_min:.2f} min"',
    "PRED_4": '"si registro más espaciado que este intervalo la gráfica puede mostrar un ciclo falso más lento que el real"',
    "CIERRE": ('f"Si registro cada {intervalo_max_min:.2f} min la memoria dura {MEMORIA * intervalo_max_min * 60 / 86400:.1f} '
               'días; me conviene porque cubre el ciclo del horno y la campaña completa sin perder información del proceso"'),
    "error_obtenido_C": "float(np.max(np.abs(error)))",
    "CONCLUSION_B": ('f"El error máximo obtenido fue {error_obtenido_C:.4f} °C y el predicho {error_max_C:.4f} °C; quedó dentro '
                     'porque el redondeo de mi convertidor nunca se aleja más de medio escalón del valor real"'),
}


def hueco(var, resuelto, nota="✎ escribe aquí"):
    if resuelto:
        return f"{var} = {SOLUCION[var]}"
    vacio = "None" if not var.isupper() else '""'
    return f"{var} = {vacio}   # {nota}"


def md(texto):
    return nbf.v4.new_markdown_cell(texto.strip())


def code(texto, titulo=None):
    c = nbf.v4.new_code_cell(texto.strip())
    if titulo:
        c.source = f"#@title {titulo}\n" + c.source
        c.metadata["cellView"] = "form"
    return c


def ejercicio(n, var, datos, unidades, r):
    return code(f"""
# ✎ {n}a · La expresión en Python, con las variables de tus datos
{hueco(var, r)}
# ✎ {n}b · La sustitución con TUS números, el resultado y la unidad
{hueco(f"SUST_{n}", r)}
# ✎ {n}c · Lo que predice en la práctica, con tus palabras (al menos 10)
{hueco(f"PRED_{n}", r)}

revisa({n}, {var}, SUST_{n}, PRED_{n}, datos=[{", ".join(datos)}], unidades={unidades!r})
""")


def cuaderno(r=False, nombre="", codigo=""):
    herramientas = open(IDENTIDAD, encoding="utf-8").read()
    celdas = [
        md(f"""
# S0 · Cuaderno de muestra · ¿Cada cuánto registrar?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Decidir con números la **resolución** y el **intervalo de registro** de un registrador de temperatura, y
comprobar con datos reales que el error de la cuantización queda dentro de lo que predice la teoría.

## La situación
En la planta se quiere vigilar la temperatura de una línea con un registrador como el Elitech RC-5. Antes de dejarlo
grabando hay que contestar tres preguntas: ¿qué tan fino mide?, ¿cuánto dura su memoria? y ¿cada cuánto debe
registrar para no perder lo que pasa en el proceso? Cada alumno tiene un registrador y un proceso distintos: los
datos salen de su código.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero). En cada uno **escribes** la expresión en Python, la sustitución con tus números y su unidad, y lo que predice para la práctica | Tus cuatro resultados y tus predicciones |
| **B · Práctica** | 80 min | Tomas una semana de temperatura real de Guadalajara, la registras con **tu** convertidor y mides el error | Una gráfica firmada, tu conclusión y el archivo `S0_<código>.csv` |
| **Hoja de resultados** | en la práctica | Importas el CSV en tu hoja de cálculo de Google; la tabla y la gráfica se arman solas; contestas las preguntas | El reporte que entregas |

## Qué entregas y cómo se califica
1. **Este cuaderno**, al terminar la sesión, con todo ejecutado (Entorno de ejecución → Reiniciar y ejecutar todo).
   ★ 3 pts · ejercicios 2, 3 y 4, 2 pts cada uno · cierre 1 pt. Se califica que el resultado sea correcto para
   **tus** datos y que la sustitución y la predicción sean tuyas.
2. **La hoja de resultados** con el reporte, en 7 días naturales.

## Reglas
- **Archivo → Guardar una copia en Drive** antes de empezar; trabaja en tu copia.
- Completa sólo lo marcado con ✎. Ninguna celda avanza si falta algo: el mensaje dice qué.
- La revisión automática dice si el ejercicio está **completo**, no si está **bien**; eso lo califica el profesor.
- Si usas un asistente de IA, dilo en tu reporte. Las sustituciones y las respuestas deben llevar **tus** números.
"""),
        code(herramientas + "\n\nimport matplotlib.pyplot as plt\n\n"
             "def completa(valor, que):\n"
             "    if valor is None:\n"
             "        raise ValueError(f'Completa {que} (✎) y vuelve a ejecutar.')\n"
             "    return valor\n\nprint('Herramientas del curso listas.')",
             titulo="Herramientas del curso (no modificar)"),
        md("## Identificación\nTu nombre y tu código aparecen en cada gráfica y en el CSV. Sin ellos el cuaderno no avanza."),
        code(f'NOMBRE = "{nombre}"   # ✎ tu nombre completo\n'
             f'CODIGO = "{codigo}"   # ✎ tu código de alumno\n'
             'SESION = "S0"\n\n'
             'alumno = identificar(NOMBRE, CODIGO, SESION)\n'
             'print("Cuaderno de", alumno.nombre, "· código", alumno.codigo)'),
        md("""
## Parte A · Actividad en clase (30 min)
Tu registrador mide desde −20 °C hasta un máximo propio, con un convertidor de N bits; guarda hasta 32 000 lecturas y
registra cada cierto intervalo. Vigila un horno cuya temperatura sube y baja con un periodo propio. Ejecuta la celda
para ver **tus** datos.

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
lsb_C  = RANGO_C / 2 ** N_BITS
SUST_1 = "50 / 2**6 = 0.781 °C"
PRED_1 = "las lecturas sólo podrán cambiar en saltos de unas ocho décimas de grado"
```
"""),
        code("""
T_MIN_C = -20.0
RANGO_C = parametro(alumno, "rango", 50, 120, 0)       # el registrador mide de T_MIN_C a T_MIN_C + RANGO_C
N_BITS = asignar(alumno, [8, 10, 12], salto=0)
MEMORIA = 32000                                        # lecturas
INTERVALO_S = asignar(alumno, [10, 30, 60, 120, 300], salto=1)
PERIODO_MIN = parametro(alumno, "periodo", 8, 30, 1)   # periodo del ciclo del horno, en minutos
print(f"Tus datos · convertidor de {N_BITS} bits · mide de {T_MIN_C:g} a {T_MIN_C + RANGO_C:g} °C (rango {RANGO_C:g} °C) · memoria {MEMORIA} lecturas")
print(f"           intervalo de registro {INTERVALO_S} s · periodo del horno {PERIODO_MIN} min")
"""),
        md("""
### ★ Ejercicio 1 · ¿Qué tan fino mide? (3 pts)
**Para qué sirve:** la resolución es el cambio más pequeño que el registrador puede distinguir. Si es mayor que
la variación que te interesa, el registro no sirve.

El convertidor divide el rango en 2ᴺ escalones; un escalón (LSB) vale **LSB = rango / 2ᴺ**. En Python, la potencia
se escribe `2 ** N_BITS`.
"""),
        ejercicio(1, "lsb_C", ["RANGO_C", "N_BITS"], ["°C"], r),
        md("""
### Ejercicio 2 · ¿Cuánto se equivoca al redondear? (2 pts)
**Para qué sirve:** es el error que agrega el registrador aunque el sensor fuera perfecto; entra en el presupuesto
de error de la medición.

Cada lectura se redondea al escalón más cercano. Piensa: si el valor real cae justo entre dos escalones, ¿qué
fracción de un LSB es lo más lejos que puede quedar? Escribe el error máximo en °C, a partir de tu `lsb_C`.
"""),
        ejercicio(2, "error_max_C", ["lsb_C"], ["°C"], r),
        md("""
### Ejercicio 3 · ¿Cuánto dura la memoria? (2 pts)
**Para qué sirve:** define cada cuánto hay que ir a descargar el registrador o si la campaña cabe completa.

La memoria se llena cuando ha guardado todas sus lecturas, una por intervalo. Calcula ese tiempo **en días**
(un día tiene 86 400 s).
"""),
        ejercicio(3, "duracion_dias", ["MEMORIA", "INTERVALO_S"], ["día"], r),
        md("""
### Ejercicio 4 · ¿Cada cuánto registrar como máximo? (2 pts)
**Para qué sirve:** si se registra muy espaciado, el registro inventa un ciclo que no existe (aliasing) y se toman
decisiones de mantenimiento con datos falsos.

El criterio de Nyquist pide **al menos dos registros por cada periodo** del proceso. Calcula el intervalo máximo en
minutos a partir de `PERIODO_MIN`.
"""),
        ejercicio(4, "intervalo_max_min", ["PERIODO_MIN"], ["min"], r),
        md("La gráfica muestra el horno y lo que guardaría tu registrador en el límite de Nyquist."),
        code("""
t = np.linspace(0, 3 * PERIODO_MIN, 600)
T = 180 + 40 * np.sin(2 * np.pi * t / PERIODO_MIN)
tm = np.arange(0, 3 * PERIODO_MIN, intervalo_max_min)
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(t, T, label="horno")
ax.plot(tm, 180 + 40 * np.sin(2 * np.pi * tm / PERIODO_MIN), "o", label=f"registro cada {intervalo_max_min:.1f} min")
ax.set_xlabel("tiempo (min)"); ax.set_ylabel("temperatura (°C)"); ax.legend()
titulo(ax, "Registro al límite de Nyquist", alumno)
firma(fig, alumno); plt.show()
"""),
        md("""
### Cierre (1 pt)
Con tus números: si el registrador guardara una lectura **cada intervalo máximo del ejercicio 4**, ¿cuántos días
duraría la memoria? ¿Te conviene ese intervalo para una campaña de una semana? Escribe al menos 20 palabras e
incluye el número de días que calculaste.
"""),
        code(hueco("CIERRE", r) + "\n\n"
             "revisa_texto('Cierre', CIERRE, {'el número de días que dura la memoria a ese intervalo':\n"
             "             MEMORIA * intervalo_max_min * 60 / 86400})"),
        md("""
## Parte B · Práctica (80 min)
**Objetivo:** comprobar con datos reales lo que predijiste en el ejercicio 2.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos | 10 | Descarga una semana de temperatura real de Guadalajara, hora por hora ([Open-Meteo](https://open-meteo.com/), CC BY 4.0). La semana depende de tu código |
| B2 · Registro | 20 | La registras con **tu** convertidor y comparas la señal real con la registrada |
| B3 · Error | 20 | Calculas el error máximo obtenido y lo comparas con el predicho |
| B4 · Conclusión | 20 | Escribes qué encontraste, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
        code("""
import json, urllib.request, datetime as dt
lunes = dt.date(2025, 1, 6) + dt.timedelta(weeks=int(alumno.codigo) % 50)
domingo = lunes + dt.timedelta(days=6)
url = ("https://archive-api.open-meteo.com/v1/archive?latitude=20.67&longitude=-103.35"
       f"&start_date={lunes}&end_date={domingo}&hourly=temperature_2m&timezone=America%2FMexico_City")
try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        d = json.load(resp)["hourly"]
    fechas, T_real = d["time"], np.array(d["temperature_2m"], dtype=float)
    FUENTE = "Open-Meteo (ERA5), Guadalajara"
except Exception as e:
    print("⚠ No se pudo descargar de Open-Meteo:", type(e).__name__, e)
    print("⚠ Se usan datos SINTÉTICOS. Vuelve a ejecutar esta celda con internet antes de entregar.")
    h = np.arange(7 * 24)
    fechas = [f"hora {i}" for i in h]
    T_real = 20 + 7 * np.sin(2 * np.pi * (h - 9) / 24) + alumno.rng("ruido").normal(0, 0.6, h.size)
    FUENTE = "SINTÉTICOS (sin conexión)"
print(f"B1 · Semana del {lunes} al {domingo} · {len(T_real)} lecturas · fuente: {FUENTE}")
"""),
        code("""
# B2 · Registro con tu convertidor: −20 °C es la cuenta 0 y cada cuenta vale un LSB
cuentas = np.round((T_real - T_MIN_C) / lsb_C)
T_cuant = cuentas * lsb_C + T_MIN_C
error = T_cuant - T_real

fig, ax = plt.subplots(figsize=(9, 3.5))
ax.plot(T_real, label="real"); ax.step(range(len(T_cuant)), T_cuant, where="mid", label=f"registrada, {N_BITS} bits")
ax.set_ylabel("T (°C)"); ax.set_xlabel("lectura (h)"); ax.legend()
titulo(ax, "Temperatura real y registrada", alumno)
firma(fig, alumno); plt.show()
"""),
        md("""
### B3 · Error máximo obtenido
El arreglo `error` tiene la diferencia entre lo registrado y lo real en cada hora. El error máximo es el **mayor
valor absoluto** de ese arreglo. Pistas: `np.abs(...)` da el valor absoluto y `np.max(...)` el mayor.
"""),
        code(hueco("error_obtenido_C", r) + """

completa(error_obtenido_C, "el error máximo obtenido")
RESULTADOS = {"lsb_C": lsb_C, "error_predicho_C": error_max_C, "error_obtenido_C": float(error_obtenido_C)}
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.plot(error, label="error de cada lectura")
ax.axhline(error_max_C, ls="--", c="r", label="± error predicho"); ax.axhline(-error_max_C, ls="--", c="r")
ax.set_ylabel("error (°C)"); ax.set_xlabel("lectura (h)"); ax.legend(loc="upper right")
titulo(ax, "Error de cuantización", alumno)
firma(fig, alumno, RESULTADOS); plt.show()
print(f"Error predicho {error_max_C:.4f} °C · error obtenido {error_obtenido_C:.4f} °C")
"""),
        md("""
### B4 · Conclusión
¿El error obtenido quedó dentro del predicho? ¿Por qué? Escribe al menos 25 palabras e incluye tus dos valores.
"""),
        code(hueco("CONCLUSION_B", r) + "\n\n"
             "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
             "             {'el error predicho': error_max_C, 'el error obtenido': error_obtenido_C}, minimo=25)"),
        md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S0_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
        code("""
ruta = f"S0_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"fecha": fechas, "T_real_C": T_real, "T_registrada_C": T_cuant, "error_C": error},
             extra={"fuente": FUENTE, "semana": f"{lunes} a {domingo}"})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
"""),
        md("## Cierre del cuaderno\nAntes de entregar: **Entorno de ejecución → Reiniciar y ejecutar todo**. Todo debe salir ✔."),
        code("""
for k, ok in REGISTRO.items():
    print(("✔" if ok else "✘"), k if isinstance(k, str) else f"Ejercicio {k}")
print(f"\\n{alumno.nombre} · {alumno.codigo} · {SESION} · {ahora()} · fuente: {FUENTE} · huella {huella(alumno, RESULTADOS)}")
"""),
    ]
    nb = nbf.v4.new_notebook()
    nb.cells = celdas
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["colab"] = {"provenance": [], "toc_visible": True}
    return nb


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--resuelto":
        nbf.write(cuaderno(True, "Alumno De Prueba", "217654321"), sys.argv[2])
        print("resuelto:", sys.argv[2])
    else:
        nbf.write(cuaderno(), SALIDA)
        print("plantilla:", SALIDA)
