# Plantillas · sesión 0

Muestra completa de cómo se arma el trabajo de una sesión. Los cuadernos y hojas de las ocho sesiones siguen esta estructura.

| Archivo | Qué es |
|---|---|
| [`S0_AC_CLASE_Colab_PLANTILLA.ipynb`](S0_AC_CLASE_Colab_PLANTILLA.ipynb) | Cuaderno de muestra: herramientas · identificación · parte A (cuatro ejercicios, ★ primero) · parte B (temperatura de Guadalajara de Open-Meteo, cuantizada con el convertidor del alumno) · CSV firmado · cierre con huella |
| [`S0_AC_PRACT_Hoja_de_resultados_PLANTILLA.xlsx`](S0_AC_PRACT_Hoja_de_resultados_PLANTILLA.xlsx) | Hoja de resultados de muestra; al subirla a Drive se abre como hoja de cálculo de Google |
| `gen_cuaderno_plantilla.py` | Genera el cuaderno; `--resuelto RUTA` produce la versión resuelta para probarla (no se sube) |
| `gen_hoja_plantilla.py` | Genera la hoja a partir de un CSV firmado de ejemplo |

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/plantillas/S0_AC_CLASE_Colab_PLANTILLA.ipynb)

Probado así: la versión resuelta corre de principio a fin (sin internet usa datos sintéticos y lo avisa); la plantilla
se detiene en la identificación con el mensaje esperado; `verificar_csv` acepta el CSV exportado; la hoja recalculada
muestra «OK» con el código correcto, «NO COINCIDE» con otro código y la leyenda con el nombre del alumno.
