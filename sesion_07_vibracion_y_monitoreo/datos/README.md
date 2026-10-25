# Datos de la sesión 7

`cwru_12k_DE.npz`: vibración del rodamiento del lado de acople (*drive end*, SKF 6205-2RS JEM) del banco de pruebas de
la Case Western Reserve University, a 12 000 muestras por segundo, 5 s por registro (60 000 muestras), unidades del
registro original (g).

| Clave | Condición | Archivo CWRU |
|---|---|---|
| `normal_0`, `normal_1`, `normal_3` | Rodamiento sano, carga de 0, 1 y 3 HP | 97, 98 y 100 (registrados a 48 kHz; aquí diezmados a 12 kHz con filtro antialias) |
| `IR007_c`, `IR021_c` | Falla en la pista interior, 0.007 y 0.021 in | 105, 106, 108 · 209, 210, 212 |
| `OR007_c`, `OR021_c` | Falla en la pista exterior a las 6:00, 0.007 y 0.021 in | 130, 131, 133 · 234, 235, 237 |

`c` es la carga del motor en HP (0, 1 o 3). Cada registro tiene su velocidad en `rpm_<clave>` y su archivo de origen en
`archivo_<clave>`. El archivo 98 no trae velocidad; se usa 1772 rpm, la de la tabla de la CWRU.

Origen: Case Western Reserve University Bearing Data Center
(https://engineering.case.edu/bearingdatacenter). Los archivos .mat se tomaron el 24 de octubre de 2026 de la copia
pública https://github.com/s-whynot/CWRU-dataset, que conserva la numeración de la CWRU, porque el sitio original no
respondía desde el entorno de producción; la carga de 2 HP se omitió porque en esa copia el archivo 99 repite al 98.
La CWRU no declara licencia: se cita la fuente.
