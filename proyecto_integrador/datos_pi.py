# -*- coding: utf-8 -*-
"""Fuente única del proyecto integrador 2027 de «Sistemas de adquisición de datos».

La usan el cuaderno del proyecto (gen_pi.py), el formato del alumno (gen_formato_pi.py) y la guía. Si algo cambia
aquí, se regeneran los tres.

Decisiones del profesor (25 de octubre de 2026):
- El proyecto es INDIVIDUAL, como el resto del curso, y sigue la estructura del de Sensores 2027: cuatro campos al
  cierre de cada sesión (se revisan, no se califican) y cuatro secciones finales; se entrega una vez, como reporte
  final (30 % del curso).
- En lugar de la propuesta y el esquema de Sensores, aquí van el PLAN DE ADQUISICIÓN para una variable del trabajo y
  su CONTRASTE CON UN REGISTRO REAL.
- El registro real se elige entre tres fuentes: un Govee H5075 en préstamo (hay 10), datos del área de trabajo (con
  permiso y anonimizados) o una de las tres campañas RC-5 del grupo.
"""

CURSO = "Sistemas de adquisición de datos"
PROGRAMA = "TSU en Electrónica y Pruebas · Jabil · 2027"
FORMATO = "F_Proyecto_integrador_DAQ_2027_GGT.docx"

# Cada sesión: tema, lo que se hizo (subtítulo), la ecuación de referencia que trae impresa el formato, la gráfica que
# se pega y la pregunta sobre el ámbito de trabajo. Las ecuaciones son las de los cuadernos (gen_sN.py).
SESIONES = [
    dict(n=1, tema="Datos en la industria y sistemas de adquisición",
         que="la cadena del termistor al archivo",
         ecuacion="V = Vcc·R_F/(R_T + R_F)   N = ROUND(V/q), q = Vcc/2ᴺ   kB/día = (86 400/Δt)·bytes/1000",
         grafica="La semana de temperatura original contra la reconstruida desde las cuentas del convertidor",
         pregunta="¿Qué datos se registran hoy en tu área, quién los revisa y qué decisión se toma con ellos?"),
    dict(n=2, tema="Muestreo, cuantización y registro",
         que="el intervalo que no miente",
         ecuacion="Δt ≤ P/2   ciclo falso = 1/|1/P − 1/Δt|   escalón = rango/2ᴺ   duración = memoria·Δt",
         grafica="Los 60 días registrados cada 20 a 32 horas: el ciclo falso contra el ciclo real",
         pregunta="¿Qué variable de tu área cambia más rápido, y cada cuánto se registra?"),
    dict(n=3, tema="Calibración y ajuste de curvas",
         que="la recta de dos puntos contra mínimos cuadrados",
         ecuacion="m = (y₂ − y₁)/(x₂ − x₁)   b = y₁ − m·x₁   x = (y − b)/m",
         grafica="La calibración del potenciómetro: puntos, recta ajustada y su rango útil",
         pregunta="¿Qué instrumento de tu área se calibra o se verifica, cada cuánto y contra qué patrón?"),
    dict(n=4, tema="Error e incertidumbre",
         que="¿mi registrador dice lo mismo que los otros?",
         ecuacion="u_A = s/√n   u_B = a/√3   u_c = √(u_A² + u_B² + (res/√12)²)   U = 2·u_c",
         grafica="Tu RC-5 contra la referencia de los otros dos, con su incertidumbre",
         pregunta="¿Qué tolerancia tiene una medición de tu área y qué exactitud tiene el instrumento que la mide?"),
    dict(n=5, tema="Ruido, filtrado y tendencias",
         que="filtrar sin perder lo que importa",
         ecuacion="σ_f = σ/√N   retraso = (N − 1)·Δt/2   días al límite = (límite − T)/m",
         grafica="El registro horario, su promedio móvil y la recta de la tendencia",
         pregunta="¿Qué variable de tu área se desvía poco a poco hasta salirse de rango, y en cuánto tiempo?"),
    dict(n=6, tema="Series de tiempo y pronóstico",
         que="el pronóstico de mañana y su error",
         ecuacion="x̂ = μ + φ·(x_hoy − μ)   MAE = promedio|real − x̂|   RMSE = √promedio(real − x̂)²",
         grafica="El pronóstico un día adelante contra lo real y contra la persistencia",
         pregunta="¿Qué valor de tu área convendría conocer con un día de anticipación, y qué harían con él?"),
    dict(n=7, tema="Monitoreo basado en condición: vibración",
         que="la huella de un rodamiento que falla",
         ecuacion="BPFO = (n/2)·f_r·(1 − d/D)   v_RMS = 1000·A/(√2·2π·f_r) mm/s   umbral = media + 3·s",
         grafica="El RMS de los casos contra el umbral de alarma de la línea base",
         pregunta="¿Qué máquina rotatoria de tu área detiene la línea si falla, y cómo se vigila hoy?"),
    dict(n=8, tema="Mantenimiento predictivo e IA",
         que="cuánto le queda y cuánto cuesta equivocarse",
         ecuacion="RUL = (U − HI)/m   precisión = VP/(VP + FP)   sensibilidad = VP/(VP + FN)",
         grafica="La vida remanente de un motor: la recta contra lo real",
         pregunta="¿Qué falla de tu área convendría anticipar, y qué cuesta una falsa alarma frente a una falla no detectada?"),
]

CAMPOS_SESION = [
    ("Lo que calculé, y con qué datos", "La variable, de dónde salieron los datos (sintéticos, públicos o medidos) y el "
     "resultado principal de tu cuaderno, con su unidad."),
    ("La ecuación que me llevo", "La de la sesión que más usaste, con tus números sustituidos y tu resultado."),
    ("En mi ámbito de trabajo", "La respuesta a la pregunta de la sesión."),
    ("La gráfica de la sesión", "La de la práctica, del cuaderno o de tu hoja de resultados, con tu nombre y tu "
     "huella."),
]

# Sección 1 · Mi plan de adquisición. Cada renglón: (campo, qué se escribe, sesiones de donde sale).
PLAN = [
    ("La decisión que apoya", "Qué decisión se tomará con los datos y con qué tipo de mantenimiento: correctivo, "
     "preventivo, basado en condición o predictivo.", "S1 · S8"),
    ("Variable, unidad y lugar", "Qué se mide, en qué unidad y dónde, sin marcas, números de parte ni valores de la "
     "línea.", "S1"),
    ("Fenómeno más rápido y su periodo P", "El cambio más rápido que interesa ver (un ciclo de compresor, una puerta, "
     "un turno) y cada cuánto se repite.", "S2"),
    ("Intervalo Δt", "El intervalo de registro y cómo cumple las tres reglas: no más rápido que el equipo, no más lento "
     "que P/2, y que la memoria alcance.", "S2"),
    ("Instrumento", "Su resolución y su exactitud (de la hoja de datos) contra la exactitud que necesita la decisión.",
     "S2 · S4"),
    ("Verificación", "Contra qué se compara el instrumento y cada cuánto: un patrón, otro equipo o una "
     "intercomparación.", "S3 · S4"),
    ("Duración y archivo", "Cuánto dura el registro, cuántas lecturas da y cuánto ocupa el archivo.", "S1 · S2"),
    ("Tratamiento", "La ventana del promedio móvil, cuánto ruido quita y cuánto retrasa; cómo se estima la tendencia.",
     "S5"),
    ("Pronóstico", "Si hace falta anticipar, con qué modelo y contra qué se compara (la persistencia).", "S6"),
    ("Umbral de alarma", "El límite, el tiempo de confirmación y la histéresis; de dónde salen.", "S7"),
    ("Costo de equivocarse", "Qué cuesta una falsa alarma y qué cuesta una falla no detectada.", "S8"),
]

# Los números del plan que se copian al cuaderno del proyecto: (variable del cuaderno, qué es, unidad, sesión)
NUMEROS_PLAN = [
    ("P_PLAN_S", "Periodo del fenómeno más rápido", "s", "S2"),
    ("DT_PLAN_S", "Intervalo de registro", "s", "S2"),
    ("EXACT_REQ", "Exactitud que necesita la decisión (±)", "unidad de la variable", "S4"),
    ("EXACT_INSTR", "Exactitud del instrumento, de su hoja de datos (±)", "unidad de la variable", "S4"),
    ("LIMITE", "Límite de la alarma", "unidad de la variable", "S7"),
    ("SENTIDO", "La alarma avisa si el valor va «arriba» o «abajo» del límite", "—", "S7"),
    ("CONFIRMA_MIN", "Tiempo de confirmación", "min", "S7"),
    ("HISTERESIS", "Histéresis: cuánto debe regresar el valor para apagar la alarma", "unidad de la variable", "S7"),
    ("VENTANA_MIN", "Ventana del promedio móvil", "min", "S5"),
]
OTRA_VARIABLE = ("Si tu registro es de otra variable o de otro lugar (un Govee o una campaña), el cuaderno usa los "
                 "números de tu plan aplicados a ESE registro: escribe en la segunda columna los que corresponden a "
                 "ese lugar y explica en la conclusión qué de lo que aprendiste aplica a tu variable.")

# Predicciones que el alumno escribe ANTES de ver su registro; el cuaderno las compara con lo obtenido.
PREDICCIONES = [
    ("PRED_MIN", "Valor mínimo que esperas en el registro", "unidad de la variable"),
    ("PRED_MAX", "Valor máximo que esperas en el registro", "unidad de la variable"),
    ("PRED_CICLO_H", "Periodo del ciclo más visible que esperas (un día = 24)", "h"),
    ("PRED_TEND", "Tendencia que esperas (0 si crees que no hay)", "unidad por día"),
    ("PRED_ALARMAS", "Alarmas que esperas con tu tiempo de confirmación y tu histéresis", "número"),
]

CADENA = [("La variable", "S1"), ("El sensor y el registrador", "S1 · S2"), ("El archivo", "S1 · S2"),
          ("El análisis", "S5 · S6"), ("La alarma", "S7"), ("La decisión", "S8")]

# Sección 2 · Mi registro contra mi plan
FUENTES = [
    ("Govee H5075 en préstamo", "Temperatura y humedad en tu área, 7 días. El grupo tiene 10: se prestan en cinco "
     "turnos de 7 días, el primero empieza en la semana 2 y el último termina en la 7. El archivo se exporta en CSV "
     "desde la app Govee Home."),
    ("Datos de tu área", "Un registro que ya existe en tu trabajo, con el permiso de tu jefe, anonimizado: sin marcas, "
     "números de parte, nombres ni ubicación exacta. No se sube a repositorios ni a asistentes de IA."),
    ("Una campaña RC-5 del grupo", "Uno de los tres registros de 7 días del grupo (sesión 2). Escribe tus "
     "predicciones para ese lugar antes de ver los datos y explica qué de lo que aprendas aplica a tu variable."),
]

FICHA_REGISTRO = ["Fuente (una de las tres)", "Lugar (sin datos confidenciales)", "Instrumento y su exactitud",
                  "Intervalo programado", "Inicio y fin (fecha y hora)", "Eventos anotados en la bitácora"]

CAPACIDADES = [
    "Seguir una variable por la cadena de adquisición: sensor, acondicionamiento, convertidor y archivo",
    "Elegir el intervalo de registro con Nyquist, el mínimo del equipo y la memoria",
    "Calcular el error de cuantización y distinguir resolución de exactitud",
    "Calibrar con dos puntos y con mínimos cuadrados, y juzgar si la recta basta",
    "Estimar la incertidumbre de un registrador y decidir si dos equipos son compatibles",
    "Filtrar un registro con promedio móvil, sabiendo cuánto ruido quita y cuánto retrasa",
    "Estimar una tendencia y cuánto falta para llegar a un límite",
    "Pronosticar un día adelante y medir el error contra la persistencia",
    "Fijar un umbral de alarma con una línea base y evaluarlo con precisión, sensibilidad y costo",
    "Explicar por qué un registro no coincidió con lo planeado",
]
NIVELES = ["Lo puedo hacer solo", "Lo hago con ayuda", "Lo vi hacer", "No lo hice"]

REFLEXION = [
    "¿Qué parte del curso te costó más trabajo, y qué hiciste al respecto?",
    "El error que más te enseñó, en un cálculo o en tu registro: qué pasó y qué entendiste después.",
    "Si volvieras a empezar tu proyecto, ¿qué cambiarías desde la primera semana?",
    "¿Qué de este curso vas a usar en tu trabajo el mes que entra? Sé concreto.",
]

RUBRICA = [
    ("Ocho bloques de sesión", 30, "Los cuatro campos completos en cada sesión, con tu valor y tu gráfica firmada"),
    ("Mi plan de adquisición", 25, "Los once campos con su sesión de origen, el intervalo con las tres reglas, la "
     "cadena y las predicciones escritas antes del registro"),
    ("Mi registro contra mi plan", 25, "Ficha del registro, tres gráficas firmadas con huella válida, la tabla de lo "
     "predicho contra lo obtenido, la conclusión con tus números y la decisión"),
    ("Autoevaluación y reflexión", 20, "Tabla completa y honesta, y cuatro respuestas concretas"),
]
assert sum(p for _, p, _ in RUBRICA) == 100

# Calendario: semana del curso -> qué toca del proyecto (los 10 min de revisión de cada sesión)
CALENDARIO = [
    (1, "Bloque 1. Eliges la variable de tu área para el plan."),
    (2, "Bloque 2. Eliges la fuente de tu registro (si pides un Govee, te inscribes en un turno) y escribes tus "
        "predicciones, con fecha, antes de que empiece tu registro. Empieza el primer turno de préstamo."),
    (3, "Bloque 3. Borrador de los campos del plan que salen de las sesiones 1 a 3."),
    (4, "Bloque 4. Intercomparación de los RC-5; campos de instrumento y verificación."),
    (5, "Bloque 5. Primer análisis con el cuaderno del proyecto, si tu registro ya terminó: calidad, filtro y tendencia."),
    (6, "Bloque 6. Campo de pronóstico. Empieza el último turno de préstamo."),
    (7, "Bloque 7. Umbral de alarma. Todos los registros deben estar completos."),
    (8, "Bloque 8. Cuaderno del proyecto completo: plan contra registro y decisión. Entrega en los 7 días naturales "
        "siguientes."),
]
TURNOS_GOVEE = dict(equipos=10, dias=7, primera_semana=2, ultima_semana=7)
TURNOS_GOVEE["turnos"] = TURNOS_GOVEE["ultima_semana"] - TURNOS_GOVEE["primera_semana"]   # 5 turnos: 2→3 … 6→7
TURNOS_GOVEE["lugares"] = TURNOS_GOVEE["equipos"] * TURNOS_GOVEE["turnos"]

# Instrumentos conocidos (para el cuaderno): exactitud de la hoja de datos y resolución en pantalla
INSTRUMENTOS = {
    "RC-5": dict(variable="temperatura", unidad="°C", exactitud=0.5, resolucion=0.1, dt_min_s=10, memoria=32000),
    "Govee H5075": dict(variable="temperatura y humedad", unidad="°C · %HR", exactitud=0.3, exactitud_hr=3.0,
                        resolucion=0.1),
}

ENTREGA = ("Se entrega en PDF, con el cuestionario final, en la categoría «Reporte final del proyecto» de Classroom, "
           "dentro de los 7 días naturales siguientes a la sesión 8. El CSV firmado del cuaderno del proyecto se "
           "sube en la misma tarea.")
