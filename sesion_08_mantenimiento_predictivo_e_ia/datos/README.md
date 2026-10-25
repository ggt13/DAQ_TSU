# Datos de la sesión 8

C-MAPSS, subconjunto **FD001**: motores turbofan simulados, una condición de operación (nivel del mar) y un modo de
falla (degradación del compresor de alta presión, HPC). Archivos originales comprimidos con gzip, sin ningún cambio.

| Archivo | Contenido |
|---|---|
| `train_FD001.txt.gz` | 100 motores que operan desde nuevos hasta la falla (20 631 ciclos) |
| `test_FD001.txt.gz` | 100 motores cuyo registro termina antes de la falla |
| `RUL_FD001.txt.gz` | Vida remanente real (ciclos) de cada motor de prueba al final de su registro |

Columnas separadas por espacios: unidad, ciclo, tres ajustes de operación y 21 sensores (s1 a s21). El curso usa
sobre todo **s11**, la presión estática a la salida del HPC (Ps30, psia).

Origen: NASA Prognostics Center of Excellence Data Set Repository, «Turbofan Engine Degradation Simulation Data Set»
(https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository). Referencia: A. Saxena, K. Goebel,
D. Simon y N. Eklund, «Damage Propagation Modeling for Aircraft Engine Run-to-Failure Simulation», PHM 2008. Tomado
el 25 de octubre de 2026 de la copia pública https://github.com/edwardzjl/CMAPSSData, idéntica al paquete de la NASA
(conserva su readme), porque el repositorio de la NASA no respondía desde el entorno de producción. Se cita la fuente.
