# Modelo DAQ 2027 · cómo se construye el material

Instrucciones para producir los ocho paquetes del curso con la misma filosofía que «Sensores y acondicionamiento de
señales» 2027. Documento vivo de referencia: «Instrucciones para construir el curso DAQ 2027» (Claude Docs).

## 1. Lo que se hereda de Sensores y lo que cambia

| Elemento | Sensores 2027 | DAQ 2027 |
|---|---|---|
| Exposición | 35 láminas: 21 del tema y 14 comunes | Igual; las comunes de hardware cambian (sección 5) |
| Actividad en clase (30 min) | Hoja de cálculos en Word, cuatro cálculos | Parte A del cuaderno Colab, cuatro ejercicios con huecos ✎ |
| Práctica (80 min) | Arduino; Google Sheets; por equipo | Parte B del cuaderno con datos reales; hoja de resultados de Google; individual |
| Reporte | Tabla, gráfica, foto con nombres, predicho contra medido, dos preguntas | Tabla, gráfica con el nombre, predicho (parte A) contra obtenido (parte B), dos preguntas |
| Cuestionario | Forms, 15 + 5; dos problemas salen de la clase | Igual |
| Proyecto integrador | Ocho bloques + propuesta + esquema + reflexión | Plan de adquisición para una variable del trabajo, contrastado con un registro real |

## 2. Sesión tipo (150 min)

10 revisión (en S1, encuadre) · 30 exposición · 30 actividad en clase (2 de planteamiento, cuatro ejercicios de unos
6 min con el ★ primero, 4 para ejecutar todo y entregar) · 80 práctica (bloques ≤ 70 min + 10 de «Tabla y captura»).

Rúbricas: cuaderno ★ 3 · otros tres 2 c/u · cierre 1 = 10. Hoja de resultados: tabla 2 · gráfica 3 ·
firma y captura 1 · predicho contra obtenido 3 · preguntas 1 = 10.

## 3. Estructura de cada cuaderno

1. **Objetivo y en qué consiste**: objetivo de la sesión en una frase; la situación de planta; tabla parte A,
   parte B y hoja de resultados con tiempo, qué se hace y qué produce; qué se entrega y cómo se califica; reglas.
2. **Herramientas del curso** (oculta) e **identificación**.
3. **Parte A**: tus datos; un ejemplo de cómo se llena un ejercicio con datos que no son los del alumno; cuatro
   ejercicios. Cada uno con «para qué sirve» en una frase. El ★ da la fórmula; los demás, sólo el concepto. El alumno
   escribe su resultado como número (✎ a; los alumnos no saben Python: calculan con calculadora u hoja de cálculo,
   y quien sepa puede escribir la operación), la sustitución con sus números y su unidad (✎ b) y lo que predice (✎ c);
   `revisa(n, valor, sustitucion, prediccion, datos, unidades)` detiene la celda si falta algo. Cierre escrito con
   `revisa_texto`, que nombra lo que falta sin revelar el valor esperado.
4. **Parte B**: tabla de bloques (≤ 70 min + 10 de «Tabla y captura»); datos reales asignados por código con aviso
   de la causa si hay que recurrir a los sintéticos; el alumno completa el cálculo clave y escribe su conclusión con
   sus valores; CSV firmado con `extra={"fuente": ..., ...}`.
5. **Cierre**: estado de cada ejercicio (`REGISTRO`) y huella.

`revisa` comprueba que el ejercicio esté completo, no que esté bien: la corrección la da `clave(codigo)`. La misma
sustitución, el resultado y las respuestas llevan los números de cada alumno. Donde hay que operar sobre muchos datos
(desviación estándar, medias, máximos) el cuaderno calcula e imprime, y el alumno usa esos números. Cada cuaderno
lleva la guía «Cómo se usa este cuaderno · no necesitas saber programar» (`cu.guia()`).

Prueba antes de subir: `python comun/prueba_cuadernos.py N` ejecuta la versión resuelta y la de un alumno que
escribe números con 4 cifras, con varios códigos; comprueba que la versión en blanco se detenga y que la del
profesor valide los CSV.
Los datos personales deben variar lo suficiente para que el ★ casi no se repita en el grupo (en S0, rango × bits da
35 combinaciones en 40 códigos consecutivos).

## 4. Trabajo individual

| Mecanismo | Implementación |
|---|---|
| Celda de identificación | `identificar(NOMBRE, CODIGO, SESION)` detiene el cuaderno si faltan o son de ejemplo |
| Datos sintéticos personales | `parametro(alumno, etiqueta, min, max)` y `alumno.rng(etiqueta)`; cada etiqueta es una secuencia independiente |
| Datos públicos asignados | `asignar(alumno, opciones, salto)`: estación, semana, rodamiento o unidad por código |
| Datos experimentales | Archivo propio `S#_<código>_<apellido>.csv`; con registrador compartido, canal o ventana por alumno |
| Firma | `titulo(ax, texto, alumno)` y `firma(fig, alumno, resultados)` en toda gráfica que se entrega |
| Huella | `huella(alumno, resultados)`: 6 caracteres de sha256 sobre código, sesión y resultados a 4 cifras |
| CSV firmado | `exportar_csv(...)`; el profesor usa `leer_csv_firmado` y `verificar_csv` |
| Hoja de resultados | B1 nombre, B2 código, verificación contra el CSV en rojo o verde, encabezados `="Obtenido · "&B1` |
| Clave del profesor | `clave(codigo)` en el cuaderno PROF (fuera del repositorio) con la tabla de todo el grupo |
| Preguntas con dato propio | El cierre y las preguntas del reporte piden citar los valores del alumno |

## 5. Fuentes de datos

Regla: la parte A usa datos sintéticos con la semilla del alumno; la parte B, datos experimentales o públicos asignados
por código. Fuentes, licencias y regla de asignación en [`FUENTES_DE_DATOS.md`](FUENTES_DE_DATOS.md). Todo conjunto
público se guarda recortado en `sesion_NN_tema/datos/` y el cuaderno lo usa si la fuente original no responde.

## 6. Piezas de cada paquete

| Pieza | Archivo |
|---|---|
| Presentación del tema, 35 láminas | `S#_PRESENT_DIAP_DAQ_2027_GGT.pptx` (+ PDF) |
| Láminas de la actividad en clase | `S#_AC_CLASE_DIAP_{PROF,ALUMNO}.pptx` |
| Cuaderno de la sesión | `sesion_NN_tema/S#_AC_CLASE_Colab_ALUMNO.ipynb` (repositorio) · `S#_AC_CLASE_Colab_PROF.ipynb` (sólo Drive) |
| Láminas de la práctica | `S#_AC_PRACT_DIAP_{PROF,ALUMNO}.pptx` |
| Hoja de resultados | `S#_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` (repositorio y Drive, convertida a hoja de cálculo de Google) · versión PROF sólo en Drive |
| Hoja de práctica y ejemplo | `S#_AC_PRACT_Hoja_de_practica.docx` · `S#_AC_PRACT_Ejemplo_de_reporte_PROF.docx` |
| Ficha de datos | `S#_Ficha_de_datos.pdf`: origen, licencia, variables, unidades, frecuencia de muestreo, asignación |
| Cuestionario | `S#_CUEST_{ALUMNO,PROF}.docx` + script de Forms |
| Lista de materiales | `S#_Lista_de_materiales.pdf` |
| NotebookLM | Guiones de audio, video y retroalimentación |
| F3 | `S#_F3_Planeacion_DAQ_2027_GGT.docx` |
| Paquete | `DAQ_S#_<Tema>_2027_GGT.zip` con las fuentes |

Láminas comunes que cambian: lista de componentes → fuentes de datos y herramientas; hoja de datos → ficha del
conjunto de datos o del registrador; diagrama eléctrico → cadena de adquisición; montaje tipo Tinkercad → flujo en
pantalla cuaderno → CSV firmado → hoja de resultados.

## 7. Producción

1. [`comun/identidad.py`](../comun/identidad.py) (en el repositorio); `tsu.py`, `marco_daq.py` y `conf_daq.py` para las
   láminas viven fuera del repositorio, con el resto de las fuentes del profesor.
2. `datos_sN.py`: intervalos de los parámetros, generación de datos a partir del código, resultados
   esperados y aserciones. El generador copia este código en los dos cuadernos para que la clave nunca diverja.
3. `gen_colab.py` (nbformat): ALUMNO con huecos ✎ y PROF con soluciones y `clave(codigo)`. Modelo:
   [`plantillas/gen_cuaderno_plantilla.py`](../plantillas/gen_cuaderno_plantilla.py).
4. `gen_hoja.py` (openpyxl): pestañas Resultados y CSV. Modelo:
   [`plantillas/gen_hoja_plantilla.py`](../plantillas/gen_hoja_plantilla.py).
5. Láminas, Word, cuestionario, F3 y NotebookLM con los generadores de Sensores.

Orden: S2 (piloto) y S4, luego S1, luego S3 y S5 a S8.

### Sesiones terminadas

- **S2** (piloto, 24 de octubre): `sesion_02_muestreo_y_cuantizacion/gen_s2.py` con `comun/cuaderno.py` y
  `comun/hoja.py`. Es el modelo a seguir para las demás.
- **S1** (24 de octubre): `sesion_01_datos_y_adquisicion/gen_s1.py`; cadena termistor → divisor → ADC → archivo.
- **S3** (24 de octubre): `sesion_03_calibracion_y_ajuste/gen_s3.py`; transmisor de presión y potenciómetros 2025.
- **S4** (24 de octubre): `sesion_04_error_e_incertidumbre/gen_s4.py`; práctica con la intercomparación de los tres
  RC-5 (`prepara_intercomparacion.py` arma el CSV a partir de los archivos de ElitechLog).
- **S5** (24 de octubre): `sesion_05_ruido_y_tendencias/gen_s5.py`; equipo que se calienta (tendencia, ciclo, ruido,
  picos), promedio y mediana móviles; práctica con 60 días de Open-Meteo (ERA5). `prepara_respaldo.py` arma la copia
  de respaldo en `datos/`.
- **S6** (24 de octubre): `sesion_06_series_de_tiempo_y_pronostico/gen_s6.py`; AR(1) de la toma de aire de un
  cuarto limpio, MAE, RMSE y validez del 75 %; práctica con el SIMAJ 2022 (33 ventanas por código), elección del
  orden por AIC (tolerancia de 2) y comparación contra la persistencia. Sustituye al cuaderno del 21 de octubre.
- **S7** (25 de octubre): `sesion_07_vibracion_y_monitoreo/gen_s7.py`; BPFO, RMS, velocidad para ISO 10816-3 y
  umbral con línea base; práctica con 12 casos de la CWRU (umbral fuera de muestra, efecto de la carga, espectro de la
  envolvente). Bloque opcional con phyphox para el ventilador del grupo.
- **S8** (25 de octubre): `sesion_08_mantenimiento_predictivo_e_ia/gen_s8.py`; vida remanente, precisión,
  sensibilidad y costo; práctica con C-MAPSS FD001 (recta contra exponencial contra real, umbral por costo en 1000
  decisiones, umbral contra regresión logística en 100 motores de prueba, árbol sin límite para el sobreajuste).

Nota: la hoja busca los resultados sin distinguir mayúsculas; `exportar_csv` rechaza nombres que sólo difieren en
mayúsculas (p. ej. `U` y `u`).

## 8. Verificación de cada paquete

- [ ] Los dos cuadernos corren de principio a fin con tres códigos de prueba; con la identificación vacía, el ALUMNO se detiene con el mensaje esperado; con la identificación llena, se detiene en el ★ y dice qué falta.
- [ ] La primera celda explica el objetivo y en qué consiste el cuaderno; cada ejercicio dice para qué sirve.
- [ ] Los tres códigos dan resultados distintos y `clave(codigo)` coincide con el cuaderno resuelto.
- [ ] Toda gráfica tiene firma (`fig._firmada`) y `verificar_csv` acepta el CSV exportado.
- [ ] La hoja recalcula con un CSV de prueba: gráfica armada, leyenda con el nombre, verificación en rojo si el código no coincide.
- [ ] Cada fuente pública descarga, y la copia de respaldo funciona sin internet.
- [ ] Láminas revisadas como imagen; revisión independiente del paquete.
- [ ] Prueba del profesor: su código en Colab, el CSV importado en su hoja y una tarea de prueba en Classroom.

## 9. Decisiones pendientes

- [ ] Un cuaderno con partes A y B (propuesto) o dos por sesión.
- [ ] Uso de Gemini en Colab y cómo se declara en el reporte.
- [ ] Si Classroom ofrece «Hacer una copia para cada alumno» con archivos .ipynb; si no, el alumno guarda su copia en Drive y la adjunta.
- [ ] Al importar el CSV con «Reemplazar la hoja actual», comprobar que las fórmulas de Resultados siguen apuntando a la pestaña CSV.
- [ ] Archivo de muestra exportado de ElitechLog para escribir el lector del RC-5.
- [ ] Ventiladores para S7; registradores de temperatura y humedad opcionales.
- [ ] Programa DAQ: corregir la asignación (Colab en clase, hoja de resultados en la práctica) y validar horas y créditos.
