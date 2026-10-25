# Sesión 1 · Datos en la industria y sistemas de adquisición

**Del sensor al archivo.** Cada alumno sigue un dato por toda la cadena de adquisición con su propia resistencia fija,
temperatura de trabajo e intervalo: temperatura → resistencia del termistor NTC → voltaje del divisor → cuenta del
convertidor de 10 bits → renglón de un archivo, y calcula cuántos datos genera un sensor al día. En la práctica pasa
una semana real de temperatura de Guadalajara por su cadena, reconstruye la temperatura desde las cuentas y mide
cuánto se pierde.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_01_datos_y_adquisicion/S1_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S1_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S1_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s1.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |

| Parte | Datos |
|---|---|
| A · actividad en clase | Resistencia fija, temperatura e intervalo por código; termistor 10 kΩ, β = 3950 K, 5 V, 10 bits |
| B · práctica | Una semana de temperatura horaria de Guadalajara ([Open-Meteo](https://open-meteo.com/), CC BY 4.0), semana por código |

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
