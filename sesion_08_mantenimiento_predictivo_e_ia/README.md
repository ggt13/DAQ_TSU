# Sesión 8 · Mantenimiento predictivo e IA

**¿Cuánto le queda y cuándo intervenir?** Cada alumno recibe una bomba con su indicador de salud (velocidad de
vibración) y su tendencia, y una flota vigilada por una regla de alarma. Calcula la vida remanente, la precisión y la
sensibilidad de la alarma y su costo, y lo compara con el correctivo y el preventivo. En la práctica usa C-MAPSS FD001
de la NASA (100 motores hasta la falla): predice a mano la vida remanente de su motor con una recta y la compara con
la real y con una curva exponencial; elige un umbral de alarma por costo, y compara su umbral con un modelo de
aprendizaje automático en 100 motores que no se usaron para ajustar nada. Un árbol de decisión sin límite muestra el
sobreajuste. Cierra con la conexión de las ocho sesiones hacia el proyecto integrador.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_08_mantenimiento_predictivo_e_ia/S8_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S8_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S8_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s8.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |
| `datos/` | C-MAPSS FD001 (entrenamiento, prueba y vida remanente real), comprimido; ver `datos/README.md` |

| Parte | Datos |
|---|---|
| A · actividad en clase | Bomba, indicador de salud, tendencia, flota, matriz de confusión y costos por código |
| B · práctica | C-MAPSS FD001, NASA Prognostics Center of Excellence (Saxena et al., 2008); motor, «hoy» y costo de falla por código |

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
