"""Genera la hoja de resultados de muestra (sesión 0), vacía, lista para que el alumno importe su CSV.

Uso:
    python gen_hoja_plantilla.py                      -> S0_AC_PRACT_Hoja_de_resultados_PLANTILLA.xlsx (vacía)
    python gen_hoja_plantilla.py --ejemplo CSV SALIDA -> la misma hoja con un CSV ya importado (para probarla)

Al subirla a Drive se abre como hoja de cálculo de Google. Pestañas:
- Resultados: nombre y código que escribe el alumno; verificación contra el CSV; predicho contra obtenido;
  tabla para la gráfica (los encabezados llevan el nombre, así la leyenda lo muestra) y las preguntas del reporte.
- CSV: aquí se importa el archivo que descarga el cuaderno (Archivo → Importar → Reemplazar la hoja actual).
Cada dato se busca por su etiqueta en la pestaña CSV, no por su renglón.
"""
import csv
import os
import sys

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "S0_AC_PRACT_Hoja_de_resultados_PLANTILLA.xlsx")
RENGLONES = 7 * 24                                   # una semana, hora por hora: el tamaño lo fija la sesión
AZUL = Font(color="0000FF")                        # lo que escribe el alumno
NEGRITA = Font(bold=True)
GRIS = Font(italic=True, color="666666")
CAPTURA = PatternFill("solid", fgColor="FFF2CC")   # celdas a llenar
ROJO = PatternFill("solid", fgColor="F4CCCC")
VERDE = PatternFill("solid", fgColor="D9EAD3")

RESULTADOS = [("lsb_C", "LSB de tu convertidor (°C)"),
              ("error_predicho_C", "Error máximo predicho, ejercicio 2 (°C)"),
              ("error_obtenido_C", "Error máximo obtenido con datos reales (°C)")]


def busca(etiqueta):
    return f'=IFERROR(VLOOKUP("{etiqueta}",CSV!$A:$B,2,FALSE),"")'


def num(x):
    try:
        return float(x)
    except ValueError:
        return x


def generar(salida=SALIDA, csv_ejemplo=None):
    wb = Workbook()
    R = wb.active
    R.title = "Resultados"
    C = wb.create_sheet("CSV")
    if csv_ejemplo:
        for f in csv.reader(open(csv_ejemplo, encoding="utf-8")):
            C.append([num(x) for x in f])
    else:
        C["A1"] = "Importa aquí tu CSV: Archivo → Importar → Subir → Reemplazar la hoja actual"

    R.column_dimensions["A"].width = 46
    R.column_dimensions["B"].width = 28
    for col in "IJK":
        R.column_dimensions[col].width = 24

    R["A1"], R["A2"] = "Nombre completo ✎", "Código de alumno ✎"
    for c in ("B1", "B2"):
        R[c].font, R[c].fill = AZUL, CAPTURA
    filas = [("Código en el CSV", busca("codigo")),
             ("Verificación", '=IF(B3="","Importa tu CSV",IF(B2="","Escribe tu código",'
                              'IF(TRIM(B3&"")=TRIM(B2&""),"OK","NO COINCIDE")))'),
             ("Huella del cuaderno", busca("huella")),
             ("Sesión", busca("sesion")),
             ("Fuente de los datos", busca("fuente")),
             ("Semana", busca("semana"))]
    for i, (a, b) in enumerate(filas, start=3):
        R.cell(i, 1, a)
        R.cell(i, 2, b)
    R.conditional_formatting.add("B4", FormulaRule(formula=['B4="NO COINCIDE"'], fill=ROJO))
    R.conditional_formatting.add("B4", FormulaRule(formula=['B4="OK"'], fill=VERDE))
    R.conditional_formatting.add("B7", FormulaRule(formula=['ISNUMBER(SEARCH("SINT",B7))'], fill=ROJO))

    R["A10"] = "Predicho contra obtenido"
    R["A10"].font = NEGRITA
    for i, (clave, texto) in enumerate(RESULTADOS, start=11):
        R.cell(i, 1, texto)
        R.cell(i, 2, busca("resultado:" + clave)).number_format = "0.0000"
    R["A14"], R["B14"] = "Diferencia, obtenido contra predicho (%)", '=IF(OR(B12="",B13=""),"",(B13-B12)/B12*100)'
    R["B14"].number_format = "0.0"
    R["A15"], R["B15"] = "¿El error obtenido queda dentro de lo predicho?", '=IF(B13="","",IF(B13<=B12,"Sí","No"))'

    R["A17"] = "Preguntas del reporte ✎"
    R["A17"].font = NEGRITA
    preguntas = ["1. ¿Por qué el error obtenido no pasa de medio LSB? Usa tus números.",
                 "2. Para registrar la temperatura de un horno de reflujo (de 25 a 260 °C), ¿qué convertidor (bits) "
                 "e intervalo elegirías y por qué?"]
    for k, p in enumerate(preguntas):
        f = 18 + k
        R.cell(f, 1, p).alignment = Alignment(wrap_text=True, vertical="top")
        R.cell(f, 2).fill = CAPTURA
        R.cell(f, 2).alignment = Alignment(wrap_text=True, vertical="top")
        R.merge_cells(start_row=f, start_column=2, end_row=f, end_column=7)
        R.row_dimensions[f].height = 70
    R["A21"] = ("La gráfica se arma sola al importar tu CSV. Cambia su título por tu nombre (doble clic en el "
                "título); la leyenda ya lo toma de B1.")
    R["A21"].font = GRIS

    # Tabla para la gráfica. H2 guarda el renglón del encabezado de la tabla en la pestaña CSV.
    R["H1"], R["H2"] = "Encabezado en CSV", '=IFERROR(MATCH("fecha",CSV!$A:$A,0),"")'
    R["H1"].font = GRIS
    R["I1"], R["J1"], R["K1"] = "Lectura (h)", '="Real · "&$B$1', '="Registrada · "&$B$1'
    for c in ("I1", "J1", "K1"):
        R[c].font = NEGRITA
    for k in range(1, RENGLONES + 1):
        f = 1 + k
        # NA() y no "": las gráficas saltan #N/A, mientras que "" puede dibujarse como cero
        R.cell(f, 10, f'=IF($H$2="",NA(),IFERROR(INDEX(CSV!$B:$B,$H$2+{k})*1,NA()))')
        R.cell(f, 11, f'=IF($H$2="",NA(),IFERROR(INDEX(CSV!$C:$C,$H$2+{k})*1,NA()))')
        R.cell(f, 9, f'=IF(ISNA(J{f}),NA(),{k - 1})')
    ultimo = 1 + RENGLONES
    R.conditional_formatting.add(f"I2:K{ultimo}", FormulaRule(formula=["ISNA(I2)"], font=Font(color="FFFFFF")))

    g = LineChart()
    g.title = "Temperatura real y registrada · (tu nombre)"
    g.y_axis.title = "Temperatura (°C)"
    g.x_axis.title = "Lectura (h)"
    g.height, g.width = 9, 22
    g.add_data(Reference(R, min_col=10, max_col=11, min_row=1, max_row=ultimo), titles_from_data=True)
    g.set_categories(Reference(R, min_col=9, min_row=2, max_row=ultimo))
    R.add_chart(g, "A23")
    wb.save(salida)
    return salida


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--ejemplo":
        print(generar(sys.argv[3], sys.argv[2]))
    else:
        print(generar())
