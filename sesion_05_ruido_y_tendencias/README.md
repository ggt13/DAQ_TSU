# Sesión 5 · Ruido, filtrado y tendencias

**¿Se está calentando o es puro ruido?** Cada alumno recibe el registro de 14 días de un equipo de planta que se
calienta poco a poco (gabinete de variador, motor de bomba, tablero, prensa, fuente de poder), con su propia tendencia,
ciclo día–noche, ruido y lecturas falsas. Calcula la tendencia con los promedios del primer y del último día, los días
que faltan para llegar al límite, cuánto ruido quita el promedio móvil y cuánto se retrasa; compara promedio y mediana
móviles frente a los picos. En la práctica filtra 60 días de temperatura horaria de Guadalajara, elige la ventana que
elimina el ciclo diario, predice la tendencia con dos semanas y la compara con la recta de los 60 promedios diarios.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_05_ruido_y_tendencias/S5_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S5_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S5_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s5.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |
| `prepara_respaldo.py` | Para el profesor: descarga una vez la copia de respaldo de Open-Meteo en `datos/` |

| Parte | Datos |
|---|---|
| A · actividad en clase | Registro sintético de 14 días por código: tendencia, ciclo, ruido, picos, intervalo y ventana del filtro |
| B · práctica | 60 días de temperatura horaria de Guadalajara, reanálisis ERA5 ([Open-Meteo](https://open-meteo.com/), CC BY 4.0: citar «Open-Meteo.com» y ERA5 de Copernicus/ECMWF); ventana de fechas por código, entre el 13 de enero y el 13 de mayo de 2025 |

**Antes de la sesión (profesor):** ejecute `python prepara_respaldo.py` en Colab o en su computadora y suba
`datos/open_meteo_gdl_2025.csv` y `datos/README.md`. Si Open-Meteo no responde en clase, el cuaderno usa esa copia;
si tampoco existe, usa datos sintéticos y lo marca en rojo en la hoja de resultados.

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
