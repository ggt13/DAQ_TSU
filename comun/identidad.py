"""Herramientas comunes del curso «Sistemas de adquisición de datos» 2027.

Identificación del alumno, datos personales a partir de su código, firma de las gráficas,
huella de los resultados y CSV firmado para la hoja de resultados.

Este archivo es la fuente única: los cuadernos de cada sesión copian su contenido en la celda
«Herramientas del curso». Si se corrige aquí, se regeneran los cuadernos.
"""
import csv
import datetime as _dt
import hashlib
import zlib

import numpy as np

try:
    from zoneinfo import ZoneInfo
    _ZONA = ZoneInfo("America/Mexico_City")
except Exception:          # Python sin zoneinfo: se usa la hora del sistema
    _ZONA = None

_VALORES_DE_EJEMPLO = {"", "TU NOMBRE", "NOMBRE APELLIDO", "000000000", "123456789"}


class Alumno:
    """Datos de quien ejecuta el cuaderno. Se crea con identificar()."""

    def __init__(self, nombre, codigo, sesion):
        self.nombre = nombre
        self.codigo = codigo
        self.sesion = sesion

    @property
    def semilla(self):
        return int(self.codigo) % (2 ** 32)

    def rng(self, etiqueta=""):
        """Generador de números aleatorios propio del alumno.

        Cada etiqueta da una secuencia independiente: agregar un parámetro nuevo
        no cambia los que ya existían.
        """
        return np.random.default_rng([self.semilla, zlib.crc32(etiqueta.encode("utf-8"))])

    def __repr__(self):
        return f"Alumno({self.nombre!r}, {self.codigo!r}, {self.sesion!r})"


def identificar(nombre, codigo, sesion):
    """Valida la celda de identificación y devuelve el Alumno.

    Detiene el cuaderno con un mensaje claro si el nombre o el código faltan
    o se dejaron con el valor de ejemplo.
    """
    nombre = " ".join(str(nombre).split())
    codigo = str(codigo).strip()
    if nombre.upper() in _VALORES_DE_EJEMPLO or len(nombre.split()) < 2:
        raise ValueError("Escribe tu nombre completo (nombre y apellido) en NOMBRE y vuelve a ejecutar.")
    if codigo in _VALORES_DE_EJEMPLO or not codigo.isdigit() or not 7 <= len(codigo) <= 10:
        raise ValueError("Escribe tu código de alumno (sólo dígitos, de 7 a 10) en CODIGO y vuelve a ejecutar.")
    return Alumno(nombre, codigo, sesion)


def parametro(alumno, etiqueta, minimo, maximo, decimales=3):
    """Un valor personal entre minimo y maximo, siempre el mismo para el mismo código."""
    valor = alumno.rng(etiqueta).uniform(minimo, maximo)
    return round(float(valor), decimales)


def asignar(alumno, opciones, salto=0):
    """Elige una opción de la lista según el código (estación, ventana de fechas, carga del motor...)."""
    opciones = list(opciones)
    return opciones[(int(alumno.codigo) + salto) % len(opciones)]


def _redondea(valor):
    if isinstance(valor, (int, float, np.floating, np.integer)):
        return format(float(valor), ".4g")
    return str(valor)


def huella(alumno, resultados):
    """Seis caracteres que dependen del código, la sesión y los resultados (redondeados a 4 cifras)."""
    partes = [alumno.codigo, alumno.sesion] + [f"{k}={_redondea(v)}" for k, v in sorted(resultados.items())]
    return hashlib.sha256("|".join(partes).encode("utf-8")).hexdigest()[:6].upper()


def ahora():
    momento = _dt.datetime.now(_ZONA) if _ZONA else _dt.datetime.now()
    return momento.strftime("%Y-%m-%d %H:%M")


def titulo(ax, texto, alumno):
    """Título de la gráfica con el nombre del alumno."""
    ax.set_title(f"{texto} · {alumno.nombre}")


def firma(fig, alumno, resultados=None):
    """Pie de la figura: nombre · código · sesión · fecha y hora · huella.

    Toda gráfica que se entrega debe pasar por aquí.
    """
    texto = f"{alumno.nombre} · {alumno.codigo} · {alumno.sesion} · {ahora()}"
    if resultados:
        texto += f" · huella {huella(alumno, resultados)}"
    fig.text(0.01, 0.005, texto, fontsize=8, color="0.35", ha="left", va="bottom")
    fig.subplots_adjust(bottom=max(fig.subplotpars.bottom, 0.14))
    fig._firmada = True
    return fig


def exportar_csv(ruta, alumno, resultados, columnas):
    """Escribe el CSV firmado que se importa en la pestaña «CSV» de la hoja de resultados.

    Renglones 1 a 5: nombre, código, sesión, huella y fecha. Después, un renglón por resultado
    («resultado:<nombre>», valor). Luego un renglón vacío y la tabla: encabezados y datos.
    `columnas` es un diccionario {encabezado: lista de valores}, todas de la misma longitud.
    """
    largos = {len(v) for v in columnas.values()}
    if len(largos) != 1:
        raise ValueError("Todas las columnas de la tabla deben tener el mismo número de renglones.")
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nombre", alumno.nombre])
        w.writerow(["codigo", alumno.codigo])
        w.writerow(["sesion", alumno.sesion])
        w.writerow(["huella", huella(alumno, resultados)])
        w.writerow(["fecha", ahora()])
        for k, v in resultados.items():
            w.writerow([f"resultado:{k}", _redondea(v)])
        w.writerow([])
        w.writerow(list(columnas))
        for fila in zip(*columnas.values()):
            w.writerow([_redondea(x) for x in fila])
    return ruta


def leer_csv_firmado(ruta):
    """Para el profesor: devuelve (metadatos, resultados, tabla) de un CSV firmado."""
    meta, resultados, tabla = {}, {}, []
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.reader(f))
    i = 0
    while i < len(filas) and filas[i]:
        clave, valor = filas[i][0], filas[i][1]
        if clave.startswith("resultado:"):
            resultados[clave.split(":", 1)[1]] = float(valor)
        else:
            meta[clave] = valor
        i += 1
    tabla = filas[i + 1:] if i + 1 < len(filas) else []
    return meta, resultados, tabla


def verificar_csv(ruta):
    """Para el profesor: True si la huella del CSV corresponde a su código, sesión y resultados."""
    meta, resultados, _ = leer_csv_firmado(ruta)
    alumno = Alumno(meta["nombre"], meta["codigo"], meta["sesion"])
    return huella(alumno, resultados) == meta["huella"]
