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


TEXTOS = {"CIERRE", "VEREDICTO", "JUSTIFICACION", "CONCLUSION_B"}


class Huecos:
    """Lo que escribe el alumno. En la versión ALUMNO queda vacío; en la PROF y en la de prueba, resuelto."""

    def __init__(self, soluciones, resuelto):
        self.sol = soluciones
        self.resuelto = resuelto

    def __call__(self, var, nota="✎ escribe aquí", vacio=None):
        texto = var.startswith(("SUST_", "PRED_")) or var in TEXTOS
        if self.resuelto == "numero" and not texto:     # prueba: como alumno que escribe el número con 4 cifras
            return f'{var} = float(f"{{({self.sol[var]}):.4g}}")'
        if self.resuelto:
            return f"{var} = {self.sol[var]}"
        if vacio is None:   # texto: sustituciones, predicciones y respuestas escritas; lo demás, números
            vacio = '""' if texto else "None"
        return f"{var} = {vacio}   # {nota}"


def _datos(datos):
    """["P_S", ("tu desviación estándar s", "np.std(L, ddof=1)")] -> código del diccionario para revisa()."""
    partes = []
    for d in datos:
        que, expr = d if isinstance(d, tuple) else (f"tu dato {d}", d)
        partes.append(f"{que!r}: {expr}")
    return "{" + ", ".join(partes) + "}"


def ejercicio(h, n, var, datos, unidades):
    """datos: nombres de variables o (descripción, expresión). unidades: lista de textos o expresión de Python."""
    unidades = unidades if isinstance(unidades, str) else repr(unidades)
    return code(f"""
# ✎ {n}a · Tu resultado: el número que calculaste (punto decimal, al menos 3 cifras significativas)
{h(var)}
# ✎ {n}b · La sustitución con TUS números, el resultado y la unidad
{h(f"SUST_{n}")}
# ✎ {n}c · Lo que predice en la práctica, con tus palabras (al menos 10)
{h(f"PRED_{n}")}

revisa({n}, {var}, SUST_{n}, PRED_{n}, datos={_datos(datos)}, unidades={unidades})
""")


GUIA = """
## Cómo se usa este cuaderno · no necesitas saber programar
Sólo cambias lo que está después del signo **=** en los renglones marcados con ✎.

| Para… | Haz esto |
|---|---|
| Ejecutar una celda | Clic en ▶ a su izquierda (o Ctrl + Enter). Ejecuta las celdas en orden, de arriba hacia abajo |
| Escribir un número | Después del **=**, con punto decimal y sin comas de miles: `u_A = 0.0316`, `MEMORIA = 32000`. Usa al menos 3 cifras significativas |
| Escribir un texto | Entre comillas: `SUST_1 = "70 / 2^10 = 0.0684 °C"`. No borres las comillas |
| Calcular | Con calculadora o con tu hoja de cálculo. Si sabes Python puedes escribir la operación en vez del número: `+ − * /`, potencia `**`, raíz `np.sqrt(x)`, eˣ `np.exp(x)` |
| Ver tus datos | Están impresos debajo de la celda «Tus datos»; usa esos números |
| Un mensaje en rojo | Lee la **última línea**: dice qué falta. Corrige y vuelve a ejecutar esa celda |
| Antes de entregar | **Entorno de ejecución → Reiniciar y ejecutar todo**, y revisa que todo salga ✔ |
"""


def guia():
    return md(GUIA)


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
