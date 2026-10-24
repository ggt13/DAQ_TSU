# Herramientas comunes

`identidad.py` es la fuente única de lo que hace individual cada trabajo. Los cuadernos copian su contenido en la
celda «Herramientas del curso»; si se corrige aquí, se regeneran los cuadernos.

| Función | Para qué |
|---|---|
| `identificar(nombre, codigo, sesion)` | Valida la celda de identificación y devuelve el `Alumno` |
| `alumno.rng(etiqueta)` | Generador de números aleatorios propio del alumno, independiente por etiqueta |
| `parametro(alumno, etiqueta, min, max, decimales)` | Un valor personal, siempre el mismo para el mismo código |
| `asignar(alumno, opciones, salto)` | Elige estación, semana, carga o unidad según el código |
| `titulo(ax, texto, alumno)` | Título de la gráfica con el nombre |
| `firma(fig, alumno, resultados)` | Pie con nombre · código · sesión · fecha y hora · huella |
| `huella(alumno, resultados)` | Seis caracteres que dependen del código, la sesión y los resultados |
| `exportar_csv(ruta, alumno, resultados, columnas)` | CSV firmado para la hoja de resultados |
| `leer_csv_firmado(ruta)` · `verificar_csv(ruta)` | Para el profesor: leer y comprobar la huella de un CSV entregado |

Pruebas: `python test_identidad.py` (validación de la identificación, datos distintos entre alumnos, asignación,
huella, CSV firmado, detección de un resultado alterado y firma en la figura).
