"""Para el profesor: une los archivos de los tres RC-5 en un solo CSV para la práctica de la sesión 4.

Uso (en Colab o en la computadora, con los archivos exportados de ElitechLog en la misma carpeta):
    python prepara_intercomparacion.py RC5_1.xlsx RC5_2.xlsx RC5_3.xlsx
-> datos/intercomparacion_RC5.csv con columnas  minuto, RC5_1, RC5_2, RC5_3  (ventana común, intervalo común)

El lector busca en cada archivo la primera columna que se puede leer como fecha y hora y la primera columna numérica
con temperaturas plausibles (de −40 a 90 °C); así tolera los encabezados y renglones de informe que agrega ElitechLog.
Si al probarlo con un archivo real no encuentra las columnas, hay que ajustar `leer_registro` a ese formato.
"""
import io
import os
import sys

import pandas as pd


def leer_registro(ruta):
    if ruta.lower().endswith((".xls", ".xlsx")):
        crudo = pd.read_excel(ruta, header=None)
    else:   # CSV o texto con renglones de informe antes de la tabla: se detecta el separador en las últimas líneas
        texto = open(ruta, encoding="utf-8", errors="replace").read()
        lineas = [l for l in texto.splitlines() if l.strip()]
        sep = max([",", ";", "\t"], key=lambda c: sum(l.count(c) for l in lineas[-50:]))
        ancho = max(l.count(sep) for l in lineas) + 1
        crudo = pd.read_csv(io.StringIO(texto), sep=sep, header=None, names=range(ancho), engine="python")
    col_t = col_v = None
    for c in crudo.columns:
        texto = crudo[c].astype(str)
        parece_fecha = texto.str.contains(r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}", regex=True)
        if col_t is None and parece_fecha.mean() > 0.5:
            col_t = c
            continue
        num = pd.to_numeric(crudo[c].astype(str).str.replace(",", "."), errors="coerce")
        if col_v is None and num.notna().mean() > 0.5 and num.dropna().between(-40, 90).all():
            col_v = c
    if col_t is None or col_v is None:
        raise ValueError(f"{ruta}: no encontré la columna de fecha y hora o la de temperatura; ajuste leer_registro.")
    t = pd.to_datetime(crudo[col_t].astype(str), errors="coerce", format="mixed")
    v = pd.to_numeric(crudo[col_v].astype(str).str.replace(",", "."), errors="coerce")
    s = pd.Series(v.values, index=t).dropna()
    s = s[s.index.notna()].sort_index()
    return s[~s.index.duplicated()]


def unir(rutas, salida):
    series = {os.path.splitext(os.path.basename(r))[0]: leer_registro(r) for r in rutas}
    ini = max(s.index.min() for s in series.values())
    fin = min(s.index.max() for s in series.values())
    if ini >= fin:
        raise ValueError("Los registros no se traslapan en el tiempo: revise fechas y horas de los registradores.")
    paso = max(pd.Series(s.index).diff().median() for s in series.values())
    rejilla = pd.date_range(ini, fin, freq=paso)
    tabla = pd.DataFrame({k: s.reindex(rejilla, method="nearest", tolerance=paso / 2) for k, s in series.items()})
    tabla = tabla.dropna()
    tabla.insert(0, "minuto", ((tabla.index - tabla.index[0]).total_seconds() / 60).round(3))
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    tabla.to_csv(salida, index=False)
    print(f"{salida}: {len(tabla)} renglones cada {paso}, de {tabla.index[0]} a {tabla.index[-1]}")
    return salida


if __name__ == "__main__":
    unir(sys.argv[1:], os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "intercomparacion_RC5.csv"))
