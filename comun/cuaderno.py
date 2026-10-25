"""Piezas comunes para generar los cuadernos del curso (nbformat).

Cada sesión escribe su `gen_sN.py` con estas piezas, para que los ocho cuadernos tengan la misma estructura:
objetivo · herramientas · identificación · parte A · parte B · cierre.
"""
import os

import nbformat as nbf

AQUI = os.path.dirname(os.path.abspath(__file__))
IDENTIDAD = os.path.join(AQUI, "identidad.py")
REPO = "https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/"


def md(texto):
    return nbf.v4.new_markdown_cell(texto.strip())


def code(texto, titulo=None):
    c = nbf.v4.new_code_cell(texto.strip())
    if titulo:
        c.source = f"#@title {titulo}\n" + c.source
        c.metadata["cellView"] = "form"
    return c


class Huecos:
    """Lo que escribe el alumno. En la versión ALUMNO queda vacío; en la PROF y en la de prueba, resuelto."""

    def __init__(self, soluciones, resuelto):
        self.sol = soluciones
        self.resuelto = resuelto

    def __call__(self, var, nota="✎ escribe aquí", vacio=None):
        if self.resuelto:
            return f"{var} = {self.sol[var]}"
        if vacio is None:
            vacio = '""' if var.isupper() else "None"
        return f"{var} = {vacio}   # {nota}"


def ejercicio(h, n, var, datos, unidades):
    """unidades: lista de textos aceptados, o una expresión de Python (str) que la produce."""
    unidades = unidades if isinstance(unidades, str) else repr(unidades)
    return code(f"""
# ✎ {n}a · La expresión en Python, con las variables de tus datos
{h(var)}
# ✎ {n}b · La sustitución con TUS números, el resultado y la unidad
{h(f"SUST_{n}")}
# ✎ {n}c · Lo que predice en la práctica, con tus palabras (al menos 10)
{h(f"PRED_{n}")}

revisa({n}, {var}, SUST_{n}, PRED_{n}, datos=[{", ".join(datos)}], unidades={unidades})
""")


def herramientas(extra=""):
    texto = open(IDENTIDAD, encoding="utf-8").read()
    texto += ("\n\nimport matplotlib.pyplot as plt\n"
              "plt.rcParams.update({'figure.figsize': (9, 3.6), 'axes.spines.top': False, 'axes.spines.right': False})\n\n"
              "def completa(valor, que):\n"
              "    if valor is None:\n"
              "        raise ValueError(f'Completa {que} (✎) y vuelve a ejecutar.')\n"
              "    return valor\n")
    if extra:
        texto += "\n" + extra.strip() + "\n"
    texto += "\nprint('Herramientas del curso listas.')"
    return code(texto, titulo="Herramientas del curso (no modificar)")


def identificacion(sesion, nombre="", codigo=""):
    return [
        md("## Identificación\nTu nombre y tu código aparecen en cada gráfica y en el CSV. Sin ellos el cuaderno no avanza."),
        code(f'NOMBRE = "{nombre}"   # ✎ tu nombre completo\n'
             f'CODIGO = "{codigo}"   # ✎ tu código de alumno\n'
             f'SESION = "{sesion}"\n\n'
             'alumno = identificar(NOMBRE, CODIGO, SESION)\n'
             'print("Cuaderno de", alumno.nombre, "· código", alumno.codigo)'),
    ]


def cierre():
    return [
        md("## Cierre del cuaderno\nAntes de entregar: **Entorno de ejecución → Reiniciar y ejecutar todo**. Todo debe salir ✔."),
        code("""
for k, ok in REGISTRO.items():
    print(("✔" if ok else "✘"), k if isinstance(k, str) else f"Ejercicio {k}")
print(f"\\n{alumno.nombre} · {alumno.codigo} · {SESION} · {ahora()} · fuente: {FUENTE} · huella {huella(alumno, RESULTADOS)}")
"""),
    ]


def guardar(celdas, ruta):
    nb = nbf.v4.new_notebook()
    nb.cells = celdas
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["colab"] = {"provenance": [], "toc_visible": True}
    nbf.write(nb, ruta)
    return ruta
