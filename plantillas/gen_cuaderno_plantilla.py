"""Genera el cuaderno de muestra del curso DAQ 2027 (sesión 0 · plantilla).

Uso:
    python gen_cuaderno_plantilla.py                  -> S0_AC_CLASE_Colab_PLANTILLA.ipynb (con huecos ✎)
    python gen_cuaderno_plantilla.py --resuelto RUTA  -> versión resuelta para probarla (no se sube al repositorio)

Muestra la estructura que deben seguir los cuadernos de las ocho sesiones:
herramientas del curso · identificación · parte A (cuatro ejercicios, ★ primero) · parte B (datos reales,
CSV firmado) · cierre con huella.
"""
import os
import sys

import nbformat as nbf

AQUI = os.path.dirname(os.path.abspath(__file__))
IDENTIDAD = os.path.join(AQUI, "..", "comun", "identidad.py")
SALIDA = os.path.join(AQUI, "S0_AC_CLASE_Colab_PLANTILLA.ipynb")
COLAB = ("https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/"
         "plantillas/S0_AC_CLASE_Colab_PLANTILLA.ipynb")

# Huecos del alumno: (variable, expresión de la solución)
HUECOS = {
    "lsb_C": "RANGO_C / 2 ** N_BITS",
    "error_max_C": "lsb_C / 2",
    "duracion_dias": "MEMORIA * INTERVALO_S / 86400",
    "intervalo_max_min": "PERIODO_MIN / 2",
}


def hueco(var, resuelto):
    return f"{var} = {HUECOS[var]}" if resuelto else f"{var} = None   # ✎ escribe aquí la expresión"


def md(texto):
    return nbf.v4.new_markdown_cell(texto.strip())


def code(texto, titulo=None):
    c = nbf.v4.new_code_cell(texto.strip())
    if titulo:
        c.source = f"#@title {titulo}\n" + c.source
        c.metadata["cellView"] = "form"
    return c


def cuaderno(resuelto=False, nombre="", codigo=""):
    herramientas = open(IDENTIDAD, encoding="utf-8").read()
    celdas = [
        md(f"""
# S0 · Plantilla del cuaderno de la sesión
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

Este cuaderno muestra cómo están armados los cuadernos del curso. Antes de empezar:

1. **Archivo → Guardar una copia en Drive.** Trabaja siempre en tu copia.
2. Escribe tu nombre y tu código en la celda de identificación. **Tus datos dependen de tu código**: los de tus compañeros son distintos.
3. Completa cada hueco marcado con ✎. No cambies las demás líneas.
4. Al terminar: **Entorno de ejecución → Reiniciar y ejecutar todo**, revisa que no haya errores y entrega en Classroom.
"""),
        code(herramientas + "\n\nimport matplotlib.pyplot as plt\n\n"
             "def completa(valor, ejercicio):\n"
             "    if valor is None:\n"
             "        raise ValueError(f'Completa el hueco ✎ del ejercicio {ejercicio} y vuelve a ejecutar.')\n"
             "    return valor\n\nprint('Herramientas del curso listas.')",
             titulo="Herramientas del curso (no modificar)"),
        md("## Identificación"),
        code(f'NOMBRE = "{nombre}"   # ✎ tu nombre completo\n'
             f'CODIGO = "{codigo}"   # ✎ tu código de alumno\n'
             'SESION = "S0"\n\n'
             'alumno = identificar(NOMBRE, CODIGO, SESION)\n'
             'print("Cuaderno de", alumno.nombre, "· código", alumno.codigo)'),
        md("""
## Parte A · Actividad en clase (30 min)
Un registrador de temperatura convierte el intervalo de −20 a 50 °C con un convertidor de N bits, guarda hasta
32 000 lecturas y se programa con un intervalo de registro. **Tus valores son propios**: ejecuta la celda siguiente.
"""),
        code("""
RANGO_C = 70.0                                   # de −20 a 50 °C
N_BITS = asignar(alumno, [8, 10, 12], salto=0)
MEMORIA = 32000                                  # lecturas
INTERVALO_S = asignar(alumno, [10, 30, 60, 120, 300], salto=1)
PERIODO_MIN = parametro(alumno, "periodo", 8, 30, 1)   # periodo del ciclo del horno, en minutos
print(f"N = {N_BITS} bits · intervalo de registro = {INTERVALO_S} s · periodo del proceso = {PERIODO_MIN} min")
"""),
        md("""
### ★ Ejercicio 1 · Resolución del registrador (3 pts)
¿Cuántos grados vale un escalón del convertidor (LSB)?  LSB = rango / 2ᴺ.

*Lo que predice en la práctica:* las lecturas sólo pueden cambiar en saltos de un LSB.
"""),
        code(hueco("lsb_C", resuelto) + "\n\nprint(f'LSB = {completa(lsb_C, 1):.4f} °C')"),
        md("""
### Ejercicio 2 · Error máximo de cuantización (2 pts)
El error de redondear al escalón más cercano nunca pasa de medio LSB.

*Lo que predice en la práctica:* en la parte B, el error máximo observado no debe pasar de este valor.
"""),
        code(hueco("error_max_C", resuelto) + "\n\nprint(f'Error máximo = {completa(error_max_C, 2):.4f} °C')"),
        md("""
### Ejercicio 3 · ¿Cuánto dura la memoria? (2 pts)
Duración = número de lecturas × intervalo. Exprésala en días (1 día = 86 400 s).
"""),
        code(hueco("duracion_dias", resuelto) + "\n\nprint(f'La memoria se llena en {completa(duracion_dias, 3):.2f} días')"),
        md("""
### Ejercicio 4 · Intervalo máximo de registro (2 pts)
Para no perder el ciclo del proceso hay que registrar al menos dos veces por periodo (criterio de Nyquist).
Calcula el intervalo máximo en minutos y revisa la gráfica: los puntos naranjas son lo que guardaría el registrador.
"""),
        code(hueco("intervalo_max_min", resuelto) + """

completa(intervalo_max_min, 4)
t = np.linspace(0, 3 * PERIODO_MIN, 600)
T = 180 + 40 * np.sin(2 * np.pi * t / PERIODO_MIN)
tm = np.arange(0, 3 * PERIODO_MIN, intervalo_max_min)
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(t, T, label="proceso")
ax.plot(tm, 180 + 40 * np.sin(2 * np.pi * tm / PERIODO_MIN), "o", label=f"registro cada {intervalo_max_min:.1f} min")
ax.set_xlabel("tiempo (min)"); ax.set_ylabel("temperatura (°C)"); ax.legend()
titulo(ax, "Registro al límite de Nyquist", alumno)
firma(fig, alumno); plt.show()
"""),
        md("""
### Cierre (1 pt)
Escribe en esta celda, con tus números: si tu registrador guardara una lectura cada intervalo máximo del ejercicio 4,
¿cuántos días duraría la memoria? ¿Te conviene ese intervalo? ✎
"""),
        md("""
## Parte B · Práctica (80 min)
Temperatura real de Guadalajara, hora por hora, en una semana que depende de tu código
([Open-Meteo](https://open-meteo.com/), licencia CC BY 4.0). Si no hay internet, el cuaderno usa datos sintéticos y lo dice.
Vas a cuantizarla con **tu** convertidor y comparar el error obtenido con el que predijiste en el ejercicio 2.
"""),
        code("""
import json, urllib.request, datetime as dt
lunes = dt.date(2025, 1, 6) + dt.timedelta(weeks=int(alumno.codigo) % 50)
domingo = lunes + dt.timedelta(days=6)
url = ("https://archive-api.open-meteo.com/v1/archive?latitude=20.67&longitude=-103.35"
       f"&start_date={lunes}&end_date={domingo}&hourly=temperature_2m&timezone=America%2FMexico_City")
try:
    with urllib.request.urlopen(url, timeout=20) as r:
        d = json.load(r)["hourly"]
    fechas, T_real = d["time"], np.array(d["temperature_2m"], dtype=float)
    FUENTE = "Open-Meteo (ERA5), Guadalajara"
except Exception as e:
    h = np.arange(7 * 24)
    fechas = [f"hora {i}" for i in h]
    T_real = 20 + 7 * np.sin(2 * np.pi * (h - 9) / 24) + alumno.rng("ruido").normal(0, 0.6, h.size)
    FUENTE = "datos sintéticos (sin conexión)"
print(f"Semana del {lunes} al {domingo} · {len(T_real)} lecturas · fuente: {FUENTE}")
"""),
        code("""
# Cuantización con tu convertidor: −20 °C es la cuenta 0
cuentas = np.round((T_real + 20) / lsb_C)
T_cuant = cuentas * lsb_C - 20
error = T_cuant - T_real
error_obtenido_C = float(np.max(np.abs(error)))

fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5.5), sharex=True)
a1.plot(T_real, label="real"); a1.step(range(len(T_cuant)), T_cuant, where="mid", label=f"{N_BITS} bits")
a1.set_ylabel("T (°C)"); a1.legend(); titulo(a1, "Temperatura real y cuantizada", alumno)
a2.plot(error); a2.axhline(error_max_C, ls="--", c="r"); a2.axhline(-error_max_C, ls="--", c="r")
a2.set_ylabel("error (°C)"); a2.set_xlabel("lectura (h)")
RESULTADOS = {"lsb_C": lsb_C, "error_predicho_C": error_max_C, "error_obtenido_C": error_obtenido_C}
firma(fig, alumno, RESULTADOS); plt.show()
print(f"Error predicho {error_max_C:.4f} °C · error obtenido {error_obtenido_C:.4f} °C")
"""),
        md("""
### CSV para tu hoja de resultados
La celda siguiente descarga `S0_<código>.csv`. En tu hoja de resultados: pestaña **CSV → Archivo → Importar →
Subir → Reemplazar la hoja actual**. La pestaña Resultados arma la tabla y la gráfica sola.
"""),
        code("""
ruta = f"S0_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"fecha": fechas, "T_real_C": T_real, "T_cuantizada_C": T_cuant, "error_C": error})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
"""),
        md("## Cierre del cuaderno"),
        code('print(f"{alumno.nombre} · {alumno.codigo} · {SESION} · {ahora()} · huella {huella(alumno, RESULTADOS)}")'),
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
