# Plantillas · sesión 0

Muestra completa de cómo se arma el trabajo de una sesión. Los cuadernos y hojas de las ocho sesiones siguen esta estructura.

| Archivo | Qué es |
|---|---|
| [`S0_AC_CLASE_Colab_PLANTILLA.ipynb`](S0_AC_CLASE_Colab_PLANTILLA.ipynb) | Cuaderno de muestra «¿Cada cuánto registrar?» |
| [`S0_AC_PRACT_Hoja_de_resultados_PLANTILLA.xlsx`](S0_AC_PRACT_Hoja_de_resultados_PLANTILLA.xlsx) | Hoja de resultados vacía; al subirla a Drive se abre como hoja de cálculo de Google |
| `gen_cuaderno_plantilla.py` | Genera el cuaderno; `--resuelto RUTA` produce la versión resuelta para probarla (no se sube) |
| `gen_hoja_plantilla.py` | Genera la hoja vacía; `--ejemplo CSV SALIDA` la genera con un CSV ya importado, para probarla |

## Cómo está armado el cuaderno

1. **Objetivo y en qué consiste**: la situación de planta, una tabla con lo que se hace en cada parte, qué se
   entrega, cómo se califica y las reglas.
2. **Herramientas del curso** (celda oculta) e **identificación**.
3. **Parte A · actividad en clase**: cuatro ejercicios, el ★ primero. Cada uno dice *para qué sirve*; el ★ da la
   fórmula y los demás sólo el concepto. El alumno escribe la expresión en Python, la sustitución con sus números y
   la unidad, y lo que predice para la práctica; `revisa()` detiene la celda si falta algo y dice qué. Cierre escrito
   con su propio número.
4. **Parte B · práctica**: tabla de bloques con tiempos; datos reales asignados por código; el alumno completa el
   cálculo del error máximo y escribe su conclusión con sus dos valores; CSV firmado con la fuente de los datos.
5. **Cierre**: estado de cada ejercicio y huella.

La revisión automática comprueba que cada ejercicio esté **completo**, no que esté bien: el resultado correcto
lo califica el profesor con la clave. Dos alumnos pueden escribir la misma expresión en Python; lo que no pueden
copiar son la sustitución, el resultado y las respuestas, porque llevan los números de cada uno.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/plantillas/S0_AC_CLASE_Colab_PLANTILLA.ipynb)

## Probado así

- La versión resuelta corre de principio a fin. Sin internet avisa la causa, usa datos sintéticos y lo marca en el
  CSV y en la hoja.
- La plantilla en blanco se detiene en la identificación; con la identificación llena, se detiene en el ejercicio 1 y
  dice qué falta.
- Una sustitución con números que no son los del alumno, un resultado distinto del que dio su expresión, la falta de
  unidad o una predicción de menos de 10 palabras detienen la celda.
- En 40 códigos consecutivos hay 35 combinaciones distintas de rango y bits.
- `verificar_csv` acepta el CSV exportado y rechaza uno con un resultado alterado.
- La hoja recalculada muestra «OK» con el código correcto, «NO COINCIDE» con otro, la fuente en rojo si los datos son
  sintéticos y la leyenda con el nombre del alumno.
