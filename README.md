# Sistemas de adquisición de datos

**TSU en Electrónica y Pruebas · Jabil · 2027** · Dr. Guillermo García Torales (CUCEI, Universidad de Guadalajara)

Cuadernos de Google Colab y datos de las ocho sesiones del curso. Las presentaciones, las hojas de cálculo, las instrucciones de cada actividad y las entregas están en Google Classroom; aquí está lo que se ejecuta.

## Sesiones

| # | Tema | Cuaderno |
|---|---|---|
| 1 | [Datos en la industria y sistemas de adquisición](sesion_01_datos_y_adquisicion/) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_01_datos_y_adquisicion/S1_AC_PR_1_1_Del_sensor_al_archivo_2027_GGT.ipynb) |
| 2 | [Muestreo, cuantización y registro](sesion_02_muestreo_y_cuantizacion/) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_02_muestreo_y_cuantizacion/S2_AC_CLASE_Colab_ALUMNO.ipynb) |
| 3 | [Calibración y ajuste de curvas](sesion_03_calibracion_y_ajuste/) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_03_calibracion_y_ajuste/S3_AC_PR_3_1_Calibracion_de_potenciometros_2027_GGT.ipynb) |
| 4 | [Calidad de la medición: error e incertidumbre](sesion_04_error_e_incertidumbre/) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_04_error_e_incertidumbre/S4_AC_CLASE_Colab_ALUMNO.ipynb) |
| 5 | [Ruido, filtrado y tendencias](sesion_05_ruido_y_tendencias/) | en preparación |
| 6 | [Series de tiempo y pronóstico](sesion_06_series_de_tiempo_y_pronostico/) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_06_series_de_tiempo_y_pronostico/S6_AC_PR_6_1_Calidad_del_aire_y_ARIMA_2027_GGT.ipynb) |
| 7 | [Monitoreo basado en condición: vibración](sesion_07_vibracion_y_monitoreo/) | en preparación |
| 8 | [Mantenimiento predictivo e IA](sesion_08_mantenimiento_predictivo_e_ia/) | en preparación |

Las sesiones 2 y 4 ya tienen el modelo que describe la sección siguiente. Los cuadernos de S1, S3 y S6 son de la
primera versión 2027 y se están adaptando; la muestra completa está en [`plantillas/`](plantillas/).

## Cómo se trabaja cada sesión

| Momento | min | Qué haces | Qué entregas |
|---|---|---|---|
| Revisión | 10 | Retroalimentación del cuestionario y avance del proyecto | — |
| Exposición | 30 | Presentación del tema | — |
| Actividad en clase | 30 | **Parte A** del cuaderno: cuatro ejercicios, el ★ primero | El cuaderno, al terminar la sesión |
| Práctica | 80 | **Parte B** del cuaderno con datos reales; el CSV que descarga va a tu hoja de resultados | La hoja de resultados con el reporte, en 7 días naturales |
| En casa | — | Cuestionario en Forms y materiales de NotebookLM | El cuestionario, en 7 días naturales |

**Todo el trabajo es individual.**

1. Abre el cuaderno con la insignia **Open in Colab** y guarda tu copia: **Archivo → Guardar una copia en Drive**.
2. Escribe tu **nombre completo y tu código** en la celda de identificación. Sin ellos el cuaderno no avanza.
3. **Tus datos dependen de tu código**: los números de tus compañeros son distintos y copiar un resultado no sirve.
4. En cada ejercicio **escribes** tres cosas: la expresión en Python, la sustitución con tus números y su unidad, y lo
   que predice para la práctica. Si falta alguna, la celda se detiene y dice qué falta.
5. Cada gráfica sale con tu nombre, tu código, la fecha y una **huella** de seis caracteres. No la borres.
6. La parte B descarga `S#_<código>.csv`. En tu hoja de resultados: pestaña **CSV → Archivo → Importar → Subir →
   Reemplazar la hoja actual**. Escribe tu nombre y tu código en la pestaña Resultados; si el código no coincide con
   el del CSV, la verificación se pone en rojo.
7. Antes de entregar: **Entorno de ejecución → Reiniciar y ejecutar todo**, sin errores.

Si usas un asistente de IA, dilo en tu reporte; las preguntas piden tus propios números.

## Calificación

| Categoría en Classroom | Peso | Tareas |
|---|---|---|
| Cuestionarios | 16 % | 8 |
| Cuestionario final | 4 % | 1 |
| Cuadernos Colab (actividad en clase) | 20 % | 8 |
| Hojas de resultados y reportes | 30 % | 8 |
| Reporte final del proyecto integrador | 30 % | 1 |

## Cómo usar este repositorio

No necesitas cuenta de GitHub ni instalar nada.

1. Entra a la carpeta de la sesión; su `README` dice qué es cada archivo.
2. Abre el cuaderno con la insignia **Open in Colab** y guarda tu copia.
3. Descarga un archivo de datos con el ícono **Download raw file**.
4. Todo el curso en un .zip: botón verde **Code → Download ZIP**.

Los archivos los sube solo el profesor; tus entregas van a Classroom. No subas datos de la planta a GitHub ni a ningún sitio público.

## Otras carpetas

| Carpeta | Qué contiene |
|---|---|
| [`comun/`](comun/) | `identidad.py`: identificación, datos por código, firma de gráficas, huella y CSV firmado; con sus pruebas |
| [`plantillas/`](plantillas/) | Cuaderno y hoja de resultados de muestra (sesión 0) y sus generadores |
| [`docs/`](docs/) | [Modelo de construcción del curso](docs/MODELO_DAQ_2027.md) y [fuentes de datos con sus licencias](docs/FUENTES_DE_DATOS.md) |

Las versiones del profesor (soluciones, claves y calificaciones) no se suben: `.gitignore` excluye todo lo que termina
en `_PROF` y las carpetas `respuestas/` y `calificaciones/`.

`zz_archivo_2024_jose_luis_becerril/` guarda, sin cambios, los archivos que subió José Luis Becerril para la generación 2024. **No forma parte del curso 2027**; se conserva como referencia. Las versiones anteriores del repositorio completo quedan en el historial: commit `e7ffed1` (curso 2024) y commit `67bd370` (versión 2025).

## Licencia

GPL-3.0. Vea el archivo `LICENSE`.
