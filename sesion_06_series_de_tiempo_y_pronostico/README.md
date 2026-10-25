# Sesión 6 · Series de tiempo y pronóstico

**¿Cuánto polvo habrá mañana?** Cada alumno recibe el PM10 diario de la toma de aire exterior de un cuarto limpio,
descrito por un modelo AR(1) con su propio promedio y memoria. Pronostica el día siguiente, calcula el MAE y el RMSE
de la semana pasada, cuenta las horas válidas de un día con códigos y decide si su promedio cuenta (75 %). En la
práctica limpia el archivo real del SIMAJ 2022 (fechas sin hora, duplicados, códigos, huecos, promedios diarios
válidos) para una estación y unas fechas asignadas por su código, pronostica a mano el primer día de prueba, elige
el modelo por su AIC y compara sus errores contra la persistencia.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_06_series_de_tiempo_y_pronostico/S6_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S6_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S6_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s6.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |
| `datos/datos_2022.xlsx` | SIMAJ 2022, el mismo archivo de 2024 y 2025 |

| Parte | Datos |
|---|---|
| A · actividad en clase | PM10 diario sintético por código (μ, φ y ruido propios) y un día hora por hora con códigos |
| B · práctica | Públicos y reales: Sistema de Monitoreo Atmosférico de Jalisco (SIMAJ), Gobierno de Jalisco, 2022, una medición por hora; 33 ventanas (estación y 60 + 14 días) asignadas por código |

Umbral de ejemplo: 50 µg/m³ de PM10 en 24 h, valor final de la NOM-025-SSA1-2021 (en 2022 regía 70 µg/m³); promedio
diario válido con al menos 18 horas (75 %, inciso 4.2.2).

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
