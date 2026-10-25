# Sesión 7 · Monitoreo basado en condición: vibración

**¿Qué le duele a la máquina?** Cada alumno recibe una máquina de planta (bomba, compresor, ventilador de torre,
chiller, manejadora de aire) con su velocidad de giro, su rodamiento y su vibración de hoy. Calcula la frecuencia de
falla de la pista exterior (BPFO), el RMS, la velocidad de vibración para la norma ISO 10816-3 y el umbral de alarma
con su línea base. En la práctica analiza vibración real del banco de rodamientos de la Case Western Reserve
University: fija el umbral con un rodamiento sano, comprueba que el dañado lo rebasa y encuentra la falla en el
espectro de la envolvente, a la frecuencia que predijo.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/sesion_07_vibracion_y_monitoreo/S7_AC_CLASE_Colab_ALUMNO.ipynb)

| Archivo | Qué es |
|---|---|
| `S7_AC_CLASE_Colab_ALUMNO.ipynb` | Cuaderno de la sesión: parte A (actividad en clase) y parte B (práctica) |
| `S7_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx` | Hoja de resultados; se sube a Drive y se abre como hoja de cálculo de Google |
| `gen_s7.py` | Genera el cuaderno, la hoja y la versión del profesor (ésta no se sube al repositorio) |
| `datos/cwru_12k_DE.npz` | 15 registros de 5 s de la CWRU (sano y cuatro fallas, cargas de 0, 1 y 3 HP); ver `datos/README.md` |

| Parte | Datos |
|---|---|
| A · actividad en clase | Máquina, velocidad, geometría del rodamiento, componentes de vibración y línea base por código |
| B · práctica | Case Western Reserve University Bearing Data Center; tipo de falla y carga del motor por código (12 casos) |
| Opcional | El ventilador del grupo medido con phyphox en el teléfono: líneas 1× y de paso de aspas; no se califica |

**Medición opcional con phyphox.** Al final de la parte B hay un bloque para subir el CSV de phyphox
(**Aceleración (sin g)**, 20 s con el teléfono fijo a la base o carcasa del ventilador). Puede hacerse como demostración
del profesor durante la exposición o en casa. El teléfono muestrea a 100–500 lecturas por segundo: basta para la 1× y
el paso de aspas, no para un rodamiento. El teléfono se coloca y se retira con el ventilador apagado y desconectado.

Las presentaciones, la hoja de práctica y el cuestionario están en Classroom.
