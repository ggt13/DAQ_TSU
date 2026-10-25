"""Sesión 1 · Datos en la industria y sistemas de adquisición. Genera:

    S1_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S1_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S1_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s1.py            -> los tres archivos
      python gen_s1.py --prueba D -> además, una versión resuelta en D para ejecutarla
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S1"
CARPETA = "sesion_01_datos_y_adquisicion"
ALUMNO = os.path.join(AQUI, "S1_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S1_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S1_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S1_AC_CLASE_Colab_ALUMNO.ipynb"

DATOS_S1 = '''
R25, BETA, VCC, N_MAX = 10000.0, 3950.0, 5.0, 1023     # termistor NTC 10 kΩ, β = 3950 K; Arduino, 10 bits
T25_K = 298.15
BYTES_LINEA = 25                                       # «2027-02-05 08:00:00,0512» y el salto de línea
RF_OPCIONES = [2200, 3300, 4700, 6800, 10000, 15000, 22000, 33000, 47000, 68000]


def datos_s1(alumno):
    return dict(RF=asignar(alumno, RF_OPCIONES), T_OBJ=parametro(alumno, "T_obj", 15, 45, 1),
                DT_S=asignar(alumno, [10, 30, 60, 120, 300, 600], salto=1))


def r_ntc(t_c):
    return R25 * np.exp(BETA * (1 / (np.asarray(t_c) + 273.15) - 1 / T25_K))


def v_div(t_c, rf):
    r = r_ntc(t_c)
    return VCC * rf / (r + rf)


def t_de_cuenta(n, rf):
    """De la cuenta del ADC a la temperatura: la cadena al revés."""
    v = np.clip(np.asarray(n, float), 0.5, N_MAX - 0.5) * VCC / N_MAX
    r = rf * (VCC / v - 1)
    return 1 / (1 / T25_K + np.log(r / R25) / BETA) - 273.15


def clave_s1(alumno):
    d = datos_s1(alumno)
    r = float(r_ntc(d["T_OBJ"]))
    v = VCC * d["RF"] / (r + d["RF"])
    return {"R_T": r, "V_T": v, "N_T": int(round(v / VCC * N_MAX)), "kB_dia": 86400 / d["DT_S"] * BYTES_LINEA / 1000}
'''

SOL = {
    "R_T": "R25 * np.exp(BETA * (1 / (T_OBJ + 273.15) - 1 / T25_K))",
    "SUST_1": 'f"10000 · e^(3950 · (1/{T_OBJ + 273.15:.2f} − 1/298.15)) = {R_T:.1f} Ω"',
    "PRED_1": '"en la práctica la resistencia del termistor bajará cuando suba la temperatura del día y subirá en la noche"',
    "V_T": "VCC * RF / (R_T + RF)",
    "SUST_2": 'f"5 × {RF} / ({R_T:.1f} + {RF}) = {V_T:.4f} V"',
    "PRED_2": '"el voltaje de salida sube cuando la temperatura sube porque la resistencia de arriba se hace más pequeña"',
    "N_T": "round(V_T / VCC * N_MAX)",
    "SUST_3": 'f"{V_T:.4f} / 5 × 1023 = {N_T} cuentas"',
    "PRED_3": '"el registrador sólo guarda números enteros así que dos temperaturas muy cercanas pueden dar la misma cuenta"',
    "kB_dia": "86400 / DT_S * BYTES_LINEA / 1000",
    "SUST_4": 'f"86400 / {DT_S} × 25 / 1000 = {kB_dia:.2f} kB"',
    "PRED_4": '"con este intervalo cada sensor genera ese volumen al día y con cientos de sensores la planta acumula mucho"',
    "CIERRE": ('f"A {T_OBJ} °C mi termistor tiene {R_T:.0f} Ω, el divisor entrega {V_T:.3f} V y el ADC guarda la cuenta '
               '{N_T}; ese número entero es lo único que llega al archivo de la planta"'),
    "V_B": "cuentas * VCC / N_MAX",
    "resol_pred_C": "(VCC / N_MAX) / S_V_C / 2",
    "CONCLUSION_B": ('f"Predije un error máximo de {resol_pred_C:.4f} °C y obtuve {error_obt_C:.4f} °C; la diferencia viene '
                     'de que la sensibilidad del divisor cambia con la temperatura a lo largo de la semana"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r or prof)
    C = [cu.md(f"""
# S1 · Datos en la industria y sistemas de adquisición · Del sensor al archivo
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Seguir un dato por toda la **cadena de adquisición** —temperatura → resistencia del sensor → voltaje → cuenta del
convertidor → renglón de un archivo— y estimar cuánto información genera un sensor en un día.

## La situación
En la planta, un termistor NTC vigila la temperatura de un proceso. Está en un divisor de tensión con una resistencia
fija `RF` y lo lee un convertidor de 10 bits (como el de un Arduino); cada lectura se guarda como un renglón de texto.
Cada alumno tiene su propia resistencia fija, su temperatura de trabajo y su intervalo de registro.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero) sobre **tu** cadena: resistencia, voltaje, cuenta y volumen de datos. En cada uno escribes la expresión, la sustitución con tus números y su unidad, y lo que predice | Tu cadena completa con números |
| **B · Práctica** | 80 min | Una semana de temperatura real de Guadalajara pasa por **tu** cadena; reconstruyes la temperatura desde las cuentas y mides cuánto se pierde | Gráficas firmadas, tu conclusión y el archivo `S1_<código>.csv` |
| **Hoja de resultados** | en la práctica | Importas el CSV en tu hoja de cálculo de Google y contestas las preguntas | El reporte que entregas |

## Qué entregas y cómo se califica
1. **Este cuaderno**, al terminar la sesión, con todo ejecutado. ★ 3 pts · ejercicios 2, 3 y 4, 2 pts cada uno ·
   cierre 1 pt. Se califica que el resultado sea correcto para **tus** datos y que la sustitución y la predicción
   sean tuyas.
2. **La hoja de resultados** con el reporte, en 7 días naturales.

## Reglas
- **Archivo → Guardar una copia en Drive** antes de empezar; trabaja en tu copia.
- Completa sólo lo marcado con ✎. Ninguna celda avanza si falta algo: el mensaje dice qué.
- La revisión automática dice si el ejercicio está **completo**, no si está **bien**; eso lo califica el profesor.
- Si usas un asistente de IA, dilo en tu reporte. Las sustituciones y las respuestas llevan **tus** números.
"""),
         cu.herramientas(DATOS_S1)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Datos comunes: termistor de `R25` = 10 000 Ω a 25 °C con `BETA` = 3950 K; alimentación `VCC` = 5 V; convertidor de
10 bits (cuenta máxima `N_MAX` = 1023); cada renglón del archivo ocupa `BYTES_LINEA` = 25 bytes. Ejecuta la celda para
ver **tus** datos.

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
V_T    = VCC * RF / (R_T + RF)
SUST_2 = "5 × 1000 / (8000 + 1000) = 0.5556 V"
PRED_2 = "con una resistencia fija tan pequeña el voltaje de salida casi no cambiará con la temperatura"
```
"""),
          cu.code("""
globals().update(datos_s1(alumno))
print(f"Tus datos · resistencia fija RF = {RF} Ω · temperatura de trabajo T_OBJ = {T_OBJ} °C · intervalo DT_S = {DT_S} s")
"""),
          cu.md("""
### ★ Ejercicio 1 · Del calor a la resistencia (3 pts)
**Para qué sirve:** es el primer eslabón: el sensor convierte la temperatura en una propiedad eléctrica.

La resistencia de un termistor NTC es **R = R25 · e^(β·(1/T − 1/T25))**, con las temperaturas en **kelvin**
(T = °C + 273.15; T25 = 298.15 K). En Python, la exponencial es `np.exp(...)`. Calcula `R_T` en Ω a tu `T_OBJ`.
"""),
          cu.ejercicio(h, 1, "R_T", [("tu temperatura en kelvin", "T_OBJ + 273.15")], ["Ω", "ohm"]),
          cu.md("""
### Ejercicio 2 · De la resistencia al voltaje (2 pts)
**Para qué sirve:** el convertidor no lee ohms, lee volts; el acondicionamiento más sencillo es un divisor de tensión.

El termistor va arriba y `RF` abajo, hacia tierra. La salida es `VCC` por la **fracción de la resistencia total que
queda abajo**. Calcula `V_T` en V.
"""),
          cu.ejercicio(h, 2, "V_T", ["RF", ("tu R_T", "R_T")], ["V"]),
          cu.md("""
### Ejercicio 3 · Del voltaje a la cuenta (2 pts)
**Para qué sirve:** lo que se guarda no es un voltaje sino un número entero: la cuenta del convertidor.

El convertidor reparte de 0 a `VCC` en cuentas de 0 a `N_MAX`. La cuenta es la fracción de `VCC` que representa tu
voltaje, multiplicada por `N_MAX` y **redondeada** a entero (`round(...)`).
"""),
          cu.ejercicio(h, 3, "N_T", [("tu V_T", "V_T")], ["cuenta"]),
          cu.md("""
### Ejercicio 4 · ¿Cuántos datos genera un sensor al día? (2 pts)
**Para qué sirve:** en la industria se registran cientos de variables; el volumen decide el almacenamiento y la
forma de analizar.

Calcula cuántos renglones se escriben en un día (86 400 s) con tu intervalo y cuántos **kB** ocupan (1 kB = 1000 bytes).
"""),
          cu.ejercicio(h, 4, "kB_dia", ["DT_S"], ["kB"]),
          cu.code("""
T = np.linspace(0, 50, 201)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
a1.plot(T, r_ntc(T) / 1000); a1.plot(T_OBJ, R_T / 1000, "o", color="#D9822B")
a1.set_xlabel("T (°C)"); a1.set_ylabel("R del termistor (kΩ)"); titulo(a1, "Sensor", alumno)
a2.plot(T, v_div(T, RF)); a2.plot(T_OBJ, V_T, "o", color="#D9822B")
a2.set_xlabel("T (°C)"); a2.set_ylabel("salida del divisor (V)"); a2.set_title(f"Divisor con RF = {RF} Ω")
firma(fig, alumno); plt.tight_layout(rect=(0, 0.06, 1, 1)); plt.show()
"""),
          cu.md("""
### Cierre (1 pt)
Describe tu cadena completa con tus números: a tu temperatura, ¿qué resistencia, qué voltaje y qué cuenta llegan al
archivo? Al menos 20 palabras, con tu voltaje y tu cuenta.
"""),
          cu.code(h("CIERRE") + "\n\nrevisa_texto('Cierre', CIERRE, {'tu voltaje': V_T, 'tu cuenta': N_T})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** pasar datos reales por tu cadena y medir cuánta información se pierde al guardar cuentas enteras.

Una semana de temperatura de Guadalajara, hora por hora ([Open-Meteo](https://open-meteo.com/), licencia CC BY 4.0);
la semana depende de tu código.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos | 10 | Descargas la semana |
| B2 · Por tu cadena | 20 | Cada hora pasa a resistencia, voltaje y cuenta, como lo guardaría el registrador |
| B3 · De regreso | 20 | Conviertes las cuentas a volts y el cuaderno reconstruye la temperatura; predices y mides el error |
| B4 · Conclusión | 20 | Comparas predicho contra obtenido, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
import json, urllib.request, datetime as dt
lunes = dt.date(2025, 1, 6) + dt.timedelta(weeks=int(alumno.codigo) % 50)
domingo = lunes + dt.timedelta(days=6)
url = ("https://archive-api.open-meteo.com/v1/archive?latitude=20.67&longitude=-103.35"
       f"&start_date={lunes}&end_date={domingo}&hourly=temperature_2m&timezone=America%2FMexico_City")
try:
    with urllib.request.urlopen(url, timeout=30) as resp:
        d = json.load(resp)["hourly"]
    fechas, T_real = d["time"], np.array(d["temperature_2m"], dtype=float)
    FUENTE = "Open-Meteo (ERA5), Guadalajara"
except Exception as e:
    print("⚠ No se pudo descargar de Open-Meteo:", type(e).__name__, e)
    print("⚠ Se usan datos SINTÉTICOS. Vuelve a ejecutar esta celda con internet antes de entregar.")
    hh = np.arange(7 * 24)
    fechas = [f"hora {i}" for i in hh]
    T_real = 20 + 7 * np.sin(2 * np.pi * (hh - 9) / 24) + alumno.rng("ruido").normal(0, 0.6, hh.size)
    FUENTE = "SINTÉTICOS (sin conexión)"
print(f"B1 · Semana del {lunes} al {domingo} · {len(T_real)} lecturas · fuente: {FUENTE}")
"""),
          cu.code("""
# B2 · Por tu cadena: temperatura → resistencia → voltaje → cuenta entera
cuentas = np.round(v_div(T_real, RF) / VCC * N_MAX).astype(int)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True)
a1.plot(T_real); a1.set_ylabel("T real (°C)"); titulo(a1, "Lo que pasó", alumno)
a2.step(range(len(cuentas)), cuentas, where="mid", color="#D9822B"); a2.set_ylabel("cuenta del ADC")
a2.set_xlabel("hora"); a2.set_title("Lo que guarda el registrador")
firma(fig, alumno); plt.show()
print(f"Cuentas de {cuentas.min()} a {cuentas.max()}: la semana usó {cuentas.max() - cuentas.min() + 1} de las 1024 posibles")
"""),
          cu.md("""
### B3 · De regreso: de la cuenta a la temperatura
1. `V_B`: el voltaje que representa cada cuenta del arreglo `cuentas` (la operación inversa del ejercicio 3).
2. El cuaderno calcula con tu `V_B` la resistencia y la temperatura reconstruida.
3. `resol_pred_C`: el **error máximo predicho**, medio escalón del convertidor expresado en °C. Un escalón vale
   `VCC / N_MAX` volts y el divisor cambia `S_V_C` volts por cada °C a la temperatura media de tu semana.
"""),
          cu.code("""
T_media = float(np.mean(T_real))
S_V_C = float((v_div(T_media + 0.5, RF) - v_div(T_media - 0.5, RF)))   # V por °C a la temperatura media
print(f"Temperatura media de tu semana: {T_media:.2f} °C · sensibilidad del divisor S_V_C = {S_V_C * 1000:.2f} mV/°C")
"""),
          cu.code(h("V_B") + "\n" + h("resol_pred_C") + """

completa(V_B, "el voltaje de cada cuenta"); completa(resol_pred_C, "el error máximo predicho")
R_B = RF * (VCC / np.asarray(V_B) - 1)
T_rec = 1 / (1 / T25_K + np.log(R_B / R25) / BETA) - 273.15
error = T_rec - T_real
error_obt_C = float(np.max(np.abs(error)))
RESULTADOS = {"R_T": float(R_T), "V_T": float(V_T), "N_T": int(N_T), "kB_dia": float(kB_dia),
              "resol_pred_C": float(resol_pred_C), "error_obt_C": error_obt_C}
fig, ax = plt.subplots()
ax.plot(error, lw=1, label="error de la temperatura reconstruida")
ax.axhline(resol_pred_C, ls="--", c="r", label="± error predicho"); ax.axhline(-resol_pred_C, ls="--", c="r")
ax.set_xlabel("hora"); ax.set_ylabel("error (°C)"); ax.legend(fontsize=8, loc="upper right")
titulo(ax, "Lo que se pierde al guardar cuentas", alumno)
firma(fig, alumno, RESULTADOS); plt.show()
print(f"Error máximo predicho {resol_pred_C:.4f} °C · obtenido {error_obt_C:.4f} °C")
"""),
          cu.md("""
### B4 · Conclusión
¿El error obtenido quedó cerca del predicho? ¿Por qué no es exactamente igual en toda la semana? Al menos 25
palabras, con tus dos valores.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'el error predicho': resol_pred_C, 'el error obtenido': error_obt_C}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S1_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
import os
ruta = f"S1_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"hora": np.arange(len(T_real)), "T_real_C": T_real, "cuenta": cuentas, "T_reconstruida_C": T_rec},
             extra={"fuente": FUENTE, "semana": f"{lunes} a {domingo}", "rf_ohm": RF})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS), f"· {os.path.getsize(ruta) / 1000:.1f} kB")
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
""")]
    C += cu.cierre()
    if prof:
        C += [cu.md("""
---
# Sólo profesor · Clave del grupo y verificación de los CSV
1. Pega en `CODIGOS` la lista de códigos del grupo y ejecuta: la tabla da los resultados esperados de la parte A.
   Tolerancia sugerida: 2 % (la cuenta, ± 1).
2. Sube los CSV entregados (ícono de carpeta) y ejecuta la última celda.
"""),
              cu.code('''
import pandas as pd, glob
CODIGOS = """
217654321
219876543
""".split()
filas = []
for c in CODIGOS:
    a = identificar("Alumno Clave", c, SESION)
    d, k = datos_s1(a), clave_s1(a)
    filas.append({"codigo": c, **d, **{x: round(float(v), 4) for x, v in k.items()}})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
for ruta in sorted(glob.glob("S1_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    k = clave_s1(identificar("Alumno Clave", meta["codigo"], SESION))
    malos = [x for x in k if x not in res or abs(res[x] - k[x]) > max(0.02 * abs(k[x]), 1.0 if x == "N_T" else 0)]
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · "
          f"fuente {meta.get('fuente')} · " + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("R_T", "★ Resistencia del termistor a tu temperatura (Ω)", "0.0"),
                    ("V_T", "Voltaje del divisor (V)", "0.0000"),
                    ("N_T", "Cuenta del convertidor", "0"),
                    ("kB_dia", "Datos por día con tu intervalo (kB)", "0.00"),
                    ("resol_pred_C", "Error máximo predicho al guardar cuentas (°C)", "0.0000"),
                    ("error_obt_C", "Error máximo obtenido en la semana (°C)", "0.0000")],
        comparacion=("resol_pred_C", "error_obt_C", "Diferencia, obtenido contra predicho (%)"),
        preguntas=["1. Sigue un dato de tu semana por toda la cadena: temperatura, resistencia, voltaje, cuenta y "
                   "temperatura reconstruida. Usa tus números.",
                   "2. Si la planta registra 500 sensores con tu intervalo, ¿cuántos MB se acumulan en un año? "
                   "¿Qué harías con tantos datos?"],
        tabla={"encabezado_csv": "hora", "x": ("A", "Hora"),
               "series": [("B", "Real"), ("D", "Reconstruida")]},
        grafica={"titulo": "Temperatura real y reconstruida desde las cuentas", "x": "Hora", "y": "Temperatura (°C)",
                 "tipo": "linea"},
        renglones=7 * 24,
        metadatos=(("Fuente de los datos", "fuente"), ("Semana", "semana"), ("Tu resistencia fija (Ω)", "rf_ohm")),
        csv_ejemplo=csv_ejemplo)


if __name__ == "__main__":
    cu.guardar(celdas(), ALUMNO)
    cu.guardar(celdas(prof=True), PROF)
    generar_hoja()
    print("listo:", ALUMNO, PROF, HOJA, sep="\n  ")
    if len(sys.argv) == 3 and sys.argv[1] == "--prueba":
        ruta = cu.guardar(celdas(r=True, nombre="Alumno De Prueba", codigo="217654321"),
                          os.path.join(sys.argv[2], "S1_resuelto.ipynb"))
        print("  prueba:", ruta)
