# Fuentes de datos del curso 2027

Tres tipos de datos, sin Arduino:

- **Sintéticos personales** (parte A de cada cuaderno): se generan con el código del alumno como semilla, con
  `comun/identidad.py`. No se guardan; el cuaderno los vuelve a crear igual cada vez.
- **Experimentales** (parte B): registradores Elitech RC-5 (temperatura, ±0.5 °C de −20 a 40 °C, resolución 0.1 °C,
  32 000 lecturas, intervalo de 10 s a 24 h; ElitechLog exporta Excel o PDF) y phyphox en el teléfono del alumno
  (acelerómetro, micrófono). Cada archivo se nombra `S#_<código>_<apellido>.csv`.
- **Públicos** (parte B): la tabla siguiente. Cada conjunto que se use se guarda recortado en `sesion_NN_tema/datos/`
  como respaldo, con su cita.

## Fuentes públicas

| Fuente | Qué ofrece | Formato y acceso | Licencia y cita | Sesiones | Asignación por código |
|---|---|---|---|---|---|
| [Open-Meteo](https://open-meteo.com/) | Clima horario desde 1940 (reanálisis ERA5) | API sin clave para uso no comercial (hasta 10 000 llamadas diarias); JSON, CSV o XLSX | CC BY 4.0: citar «Open-Meteo.com» y ERA5 | 1, 2, 5 | Semana del año o ubicación |
| [CWRU Bearing Data Center](https://engineering.case.edu/bearingdatacenter/normal-baseline-data) | Vibración de rodamientos sanos y con falla, motor de 0 a 3 HP | Archivos .mat de descarga directa | La página no declara licencia: citar Case Western Reserve University Bearing Data Center | 7 | Carga del motor y tipo de falla |
| [NASA PCoE](https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository) | Rodamientos IMS hasta la falla; motores turbofan C-MAPSS | Zip de descarga directa; algunos conjuntos del repositorio están fuera de línea | Citar NASA Prognostics Center of Excellence y el autor de cada conjunto | 8 | Rodamiento o unidad |
| [Calidad del aire de Jalisco](https://hub.tumidata.org/dataset/historical_air_quality_databases_guadalajara/resource/c6a44128-b35a-47d1-4ecc-837e52cbdb2e) | Contaminantes por estación desde 1999 (réplica del portal de datos abiertos de Jalisco) | CSV | La réplica no indica licencia: verificarla en el portal oficial antes de usarla | 6 | Estación y contaminante |

Consultadas el 24 de octubre de 2026. Conviene verificar cada enlace al inicio de cada ciclo.

## Regla para agregar una fuente

1. Abrir la página original y anotar la licencia y la forma de citarla.
2. Recortar lo que la sesión necesita y guardarlo en `sesion_NN_tema/datos/` con un README de tres líneas: origen, fecha de
   descarga y licencia.
3. En el cuaderno, intentar primero la fuente original y, si falla, la copia del repositorio; decir en pantalla cuál se usó.
4. Definir la regla de asignación con `asignar(alumno, opciones)` para que dos alumnos contiguos no compartan datos.
