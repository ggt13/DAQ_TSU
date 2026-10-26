# Proyecto integrador · Sistemas de adquisición de datos 2027

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ggt13/DAQ_TSU/blob/main/proyecto_integrador/PI_Colab_ALUMNO.ipynb)

Proyecto **individual** que acompaña las ocho sesiones (30 % del curso). Sigue la estructura del de Sensores 2027:

1. **Al cierre de cada sesión**, cuatro campos en el formato: lo que calculaste y con qué datos, la ecuación que te
   llevas con tu valor, la pregunta sobre tu ámbito de trabajo y la gráfica firmada. Se revisan en los 10 minutos de
   revisión; no se califican.
2. **Al final**, cuatro secciones: **mi plan de adquisición** para una variable de tu área, **mi registro contra mi
   plan** (con el cuaderno de esta carpeta), autoevaluación y reflexión. Se entrega una vez, en PDF, en los 7 días
   naturales siguientes a la sesión 8.

| Componente | Peso |
|---|---|
| Ocho bloques de sesión | 30 % |
| Mi plan de adquisición | 25 % |
| Mi registro contra mi plan | 25 % |
| Autoevaluación y reflexión | 20 % |

## El registro real
Cada alumno elige una fuente: un **Govee H5075** en préstamo (10 equipos, turnos de 7 días de la semana 2 a la 7), un
registro de **su área** (con permiso y anonimizado) o una de las **tres campañas RC-5** del grupo. Escribe sus
predicciones antes de ver los datos.

## Archivos
| Archivo | Qué es |
|---|---|
| `datos_pi.py` | Fuente única: sesiones, campos del plan, predicciones, fuentes, capacidades, rúbrica y calendario |
| `gen_pi.py` | Genera el cuaderno `PI_Colab_ALUMNO.ipynb` (y la versión del profesor, que va sólo a Drive) |
| `gen_formato_pi.py` | Genera el formato `F_Proyecto_integrador_DAQ_2027_GGT.docx` (y su PDF con `--pdf`) |
| `prueba_pi.py` | Prueba el cuaderno con registros tipo Govee, ElitechLog y CSV de un área, antes de subirlo |
| `prepara_campana.py` | Para el profesor: convierte el archivo de ElitechLog de una campaña al CSV que lee el cuaderno |
| `datos/` | Las tres campañas RC-5 del grupo, cuando existan |

El cuaderno lee CSV con coma o punto y coma (y coma decimal), y Excel; busca una columna con fecha y hora y las columnas
con números; convierte °F a °C si el encabezado lo dice. **Pendiente:** probarlo con un archivo real exportado de la
app Govee Home y otro de ElitechLog.
