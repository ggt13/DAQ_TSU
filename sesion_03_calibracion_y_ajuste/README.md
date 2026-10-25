# Sesión 3 · Calibración y ajuste de curvas

**De la lectura al valor verdadero.** Cada alumno calibra su propio transmisor de presión con cinco puntos contra un
patrón: pendiente y ordenada de la calibración de dos puntos, conversión de una lectura y no linealidad, y la compara
con la recta de mínimos cuadrados. En la práctica usa mediciones reales de la generación 2025: elige el rango útil de
un potenciómetro rotatorio, convierte su lectura a ángulo y la compara con la regla de tres, y decide entre recta y
polinomio para un potenciómetro deslizable mirando los residuos.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_03_calibracion_y_ajuste/S3_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S3_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S3_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s3.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |

| Parte | Datos |
|---|---|
| A · actividad en clase | Transmisor de presión por código: alcance, ganancia, offset y curvatura; cinco puntos de calibración |
| B · práctica | Mediciones reales de la generación 2025 con Arduino (10 bits, 5 V): rotatorio de 0° a 290° en subida y bajada, deslizable de 0 a 6 cm; lectura a convertir por código |

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
