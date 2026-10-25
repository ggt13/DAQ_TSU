# Sesión 4 · Calidad de la medición: error e incertidumbre

**¿Cuánto puedo confiar en mi registrador?** Cada alumno recibe un registrador (modelo, exactitud y resolución), una
referencia y sus propias lecturas; calcula la incertidumbre tipo A, la tipo B del fabricante, la combinada y la
expandida, y decide si su registrador es compatible con la referencia. En la práctica toma una hora de uno de los tres
Elitech RC-5 del grupo, colocados juntos, y lo compara con la mediana de los otros dos.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_04_error_e_incertidumbre/S4_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S4_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S4_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s4.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |
| `prepara_intercomparacion.py` | Para el profesor: une los archivos de los tres RC-5 en `datos/intercomparacion_RC5.csv` |

| Parte | Datos |
|---|---|
| A · actividad en clase | Registrador, referencia y lecturas sintéticas por código |
| B · práctica | Intercomparación de los tres RC-5 del grupo, colocados juntos; registrador y ventana de 60 min por código |

**Antes de la sesión (profesor):** coloque los tres RC-5 juntos, con el mismo intervalo (10 s), al menos 3 horas.
Exporte los tres archivos de ElitechLog y ejecute `python prepara_intercomparacion.py RC5_1.xlsx RC5_2.xlsx RC5_3.xlsx`;
suba al repositorio el `datos/intercomparacion_RC5.csv` que resulta. Mientras no exista, el cuaderno usa datos
sintéticos y lo marca en la hoja.

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
