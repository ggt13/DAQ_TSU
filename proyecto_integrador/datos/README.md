# Datos del proyecto integrador

Aquí van los registros de las **tres campañas RC-5 del grupo** (sesión 2), que el cuaderno del proyecto descarga cuando
el alumno escribe `FUENTE_REG = "campaña 1"` (o 2, o 3):

| Archivo | Qué es |
|---|---|
| `campana_1.csv`, `campana_2.csv`, `campana_3.csv` | `fecha_hora, temperatura` (°C), ya recortados a las horas en que el registrador estuvo en su lugar |
| `campanas.csv` | Una fila por campaña: lugar (sin datos confidenciales), inicio, fin, intervalo y número de lecturas |

Se arman con `python ../prepara_campana.py N archivo_de_ElitechLog.xlsx "lugar"`. Mientras un archivo no exista, el
cuaderno usa un registro **sintético** marcado como tal, y la verificación del profesor lo señala.

Los registros de Govee y los datos de las áreas de trabajo **no** se suben aquí: son de cada alumno y pueden contener
información de la empresa.
