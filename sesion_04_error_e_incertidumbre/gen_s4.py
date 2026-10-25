"""Sesión 4 · Calidad de la medición: error e incertidumbre. Genera:

    S4_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S4_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S4_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s4.py            -> los tres archivos
      python gen_s4.py --prueba D -> además, una versión resuelta en D para ejecutarla

Datos de la práctica: datos/intercomparacion_RC5.csv, que arma el profesor con prepara_intercomparacion.py a partir
de los archivos de los tres RC-5 colocados juntos. Mientras no exista, el cuaderno usa datos sintéticos y lo dice.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S4"
CARPETA = "sesion_04_error_e_incertidumbre"
ALUMNO = os.path.join(AQUI, "S4_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S4_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S4_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S4_AC_CLASE_Colab_ALUMNO.ipynb"
URL_DATOS = ("https://raw.githubusercontent.com/ggt13/DAQ_TSU/main/" + CARPETA + "/datos/intercomparacion_RC5.csv")

DATOS_S4 = f'''
URL_DATOS = "{URL_DATOS}"
MODELOS = [  # registrador, exactitud del fabricante (± °C), resolución (°C)
    ("Elitech RC-5", 0.5, 0.1),
    ("Govee H5075", 0.3, 0.1),
    ("Elitech RC-4HC", 0.5, 0.1),
]
EXACT_RC5_C, RES_RC5_C = 0.5, 0.1
VENTANA_MIN = 60


def datos_s4(alumno):
    """Los datos personales de la parte A: un registrador, una referencia y sus lecturas."""
    modelo, exact, res = asignar(alumno, MODELOS, salto=1)
    t_ref = parametro(alumno, "T_ref", 20, 30, 2)
    sesgo = parametro(alumno, "sesgo", -0.8, 0.8, 2)
    ruido = parametro(alumno, "ruido", 0.05, 0.2, 3)
    n = asignar(alumno, [10, 12, 15, 20], salto=2)
    lect = np.round((t_ref + sesgo + alumno.rng("lecturas").normal(0, ruido, n)) / res) * res
    return dict(MODELO=modelo, EXACT_C=exact, RES_C=res, T_REF=t_ref, N_LECT=n, LECTURAS=np.round(lect, 1))


def incertidumbre(lecturas, exact, res):
    """u_A, u_B, u_res, u_c y U (k = 2) de una serie de lecturas."""
    u_a = np.std(lecturas, ddof=1) / np.sqrt(len(lecturas))
    u_b = exact / np.sqrt(3)
    u_r = res / np.sqrt(12)
    u_c = np.sqrt(u_a ** 2 + u_b ** 2 + u_r ** 2)
    return u_a, u_b, u_r, u_c, 2 * u_c


def clave_s4(alumno):
    d = datos_s4(alumno)
    u_a, u_b, u_r, u_c, U = incertidumbre(d["LECTURAS"], d["EXACT_C"], d["RES_C"])
    return {{"u_A": u_a, "u_fab": u_b, "u_c": u_c, "U_exp": U, "delta_C": float(np.mean(d["LECTURAS"]) - d["T_REF"])}}


def carga_intercomparacion(alumno):
    """La tabla de los tres RC-5 (minuto + tres columnas). Si no se puede leer, datos sintéticos marcados."""
    import pandas as pd
    try:
        tabla = pd.read_csv(URL_DATOS)
        fuente = "Intercomparación de los tres RC-5 del grupo"
    except Exception as e:
        print("⚠ No se pudo leer la intercomparación del grupo:", type(e).__name__, e)
        print("⚠ Se usan datos SINTÉTICOS. Avisa al profesor antes de entregar.")
        g = np.random.default_rng(2027)
        m = np.arange(0, 180, 1 / 6)
        sala = 24 + 0.6 * np.sin(m / 50) + 0.002 * m
        tabla = pd.DataFrame({{"minuto": np.round(m, 3)}})
        for k, sesgo in zip(("RC5_1", "RC5_2", "RC5_3"), (0.15, -0.25, 0.35)):
            tabla[k] = np.round(sala + sesgo + g.normal(0, 0.05, m.size), 1)
        fuente = "SINTÉTICOS (sin datos del grupo)"
    return tabla, fuente


def ventana_s4(alumno, tabla):
    """Tu registrador, tu ventana de 60 min y la referencia (mediana de los otros dos)."""
    loggers = list(tabla.columns[1:4])
    mio = asignar(alumno, loggers, salto=0)
    otros = [k for k in loggers if k != mio]
    dur = float(tabla["minuto"].iloc[-1])
    inicio = (int(alumno.codigo) % max(1, int(dur - VENTANA_MIN))) if dur > VENTANA_MIN else 0
    v = tabla[(tabla["minuto"] >= inicio) & (tabla["minuto"] < inicio + VENTANA_MIN)]
    return mio, otros, inicio, v["minuto"].to_numpy(), v[mio].to_numpy(), v[otros].median(axis=1).to_numpy()
'''

SOL = {
    "u_A": "np.std(LECTURAS, ddof=1) / np.sqrt(len(LECTURAS))",
    "SUST_1": 'f"{np.std(LECTURAS, ddof=1):.4f} °C / √{N_LECT} = {u_A:.4f} °C"',
    "PRED_1": '"con más lecturas esta parte de la incertidumbre baja, pero no puede bajar de lo que aporta el fabricante"',
    "u_B": "EXACT_C / np.sqrt(3)",
    "SUST_2": 'f"{EXACT_C} °C / √3 = {u_B:.4f} °C"',
    "PRED_2": '"esta incertidumbre no baja aunque tome muchas lecturas porque viene de la exactitud que declara el fabricante"',
    "u_c": "np.sqrt(u_A ** 2 + u_B ** 2 + (RES_C / np.sqrt(12)) ** 2)",
    "SUST_3": 'f"√({u_A:.4f}² + {u_B:.4f}² + {RES_C / np.sqrt(12):.4f}²) = {u_c:.4f} °C"',
    "PRED_3": '"la incertidumbre combinada queda dominada por la exactitud del fabricante y casi no depende del ruido"',
    "U": "2 * u_c",
    "SUST_4": 'f"2 × {u_c:.4f} °C = {U:.4f} °C"',
    "PRED_4": '"si mi registrador es compatible, su diferencia con la referencia no debe pasar de este valor"',
    "delta_C": "np.mean(LECTURAS) - T_REF",
    "VEREDICTO": ('f"La diferencia con la referencia es {abs(delta_C):.3f} °C y mi U es {U:.3f} °C, así que mi '
                  'registrador " + ("es compatible y puede usarse" if abs(delta_C) <= U else '
                  '"no es compatible y hay que corregir su sesgo antes de usarlo") + " en una auditoría de la planta"'),
    "u_A_B": "np.std(T_mio, ddof=1) / np.sqrt(len(T_mio))",
    "U_B": "2 * np.sqrt(u_A_B ** 2 + (EXACT_RC5_C / np.sqrt(3)) ** 2 + (RES_RC5_C / np.sqrt(12)) ** 2)",
    "delta_B": "np.mean(T_mio) - np.mean(T_ref)",
    "CONCLUSION_B": ('f"Mi registrador {MIO} se separa {abs(delta_B):.3f} °C de la referencia y su U es {U_B:.3f} °C; '
                     'el sesgo pesa más que el ruido y la incertidumbre la domina la exactitud del fabricante"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# S4 · Calidad de la medición: error e incertidumbre · ¿Cuánto puedo confiar en mi registrador?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Expresar una medición como **valor ± incertidumbre** y decidir si un registrador es **compatible** con una
referencia: separar lo que aporta el ruido (tipo A) de lo que aporta el fabricante (tipo B) y combinarlos.

## La situación
Antes de confiar en un registrador para una auditoría hay que saber cuánto puede equivocarse. En clase trabajas con
las lecturas de **tu** registrador junto a un termómetro de referencia; en la práctica, con los tres Elitech RC-5 del
grupo puestos uno junto al otro, cada alumno con un registrador y una hora distintos.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero): incertidumbre tipo A, tipo B, combinada y expandida. En cada uno escribes tu resultado, la sustitución con tus números y su unidad, y lo que predice. Cierre: ¿tu registrador es compatible? | Tu resultado como valor ± U y tu veredicto |
| **B · Práctica** | 80 min | Tomas una hora de **tu** RC-5 en la intercomparación del grupo, la comparas contra la mediana de los otros dos y decides si es compatible | Gráficas firmadas, tu conclusión y el archivo `S4_<código>.csv` |
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
         cu.guia(),
         cu.herramientas(DATOS_S4)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** registrador y sus lecturas. El termómetro de referencia marcó `T_REF` durante todas
las lecturas.

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
u_A    = 0.0200
SUST_1 = "0.0800 °C / √16 = 0.0200 °C"
PRED_1 = "con más lecturas esta incertidumbre bajaría, pero sólo como la raíz del número de lecturas"
```
"""),
          cu.code("""
globals().update(datos_s4(alumno))
print(f"Tu registrador · {MODELO} · exactitud ± {EXACT_C} °C · resolución {RES_C} °C")
print(f"Referencia: T_REF = {T_REF} °C · N_LECT = {N_LECT} lecturas:")
print("LECTURAS =", ", ".join(f"{x:.1f}" for x in LECTURAS))
print(f"Media de tus lecturas = {np.mean(LECTURAS):.3f} °C · desviación estándar s = {np.std(LECTURAS, ddof=1):.4f} °C")
"""),
          cu.md("""
### ★ Ejercicio 1 · Incertidumbre tipo A (3 pts)
**Para qué sirve:** mide cuánto cambian las lecturas por el ruido. Es la parte de la incertidumbre que se reduce
tomando más lecturas.

**u_A = s / √n**, donde *s* es la desviación estándar de tus lecturas (impresa arriba) y *n* cuántas son
(`N_LECT`). En la sustitución escribe tu *s*, tu *n* y el resultado.
"""),
          cu.ejercicio(h, 1, "u_A", ["N_LECT", ("tu desviación estándar s", "np.std(LECTURAS, ddof=1)")], ["°C"]),
          cu.md("""
### Ejercicio 2 · Incertidumbre tipo B del fabricante (2 pts)
**Para qué sirve:** la exactitud que declara el fabricante (± `EXACT_C`) es un error que no se ve en las lecturas y
no baja aunque tomes muchas.

Cuando sólo se sabe que el error está dentro de ± a, con cualquier valor igual de probable, la incertidumbre es la
semiamplitud entre la raíz de tres. Calcula `u_B` en °C.
"""),
          cu.ejercicio(h, 2, "u_B", ["EXACT_C"], ["°C"]),
          cu.md("""
### Ejercicio 3 · Incertidumbre combinada (2 pts)
**Para qué sirve:** junta todo lo que puede equivocar la medición en un solo número.

Las fuentes independientes se suman **en cuadratura** (raíz de la suma de los cuadrados): tu `u_A`, tu `u_B` y la
de la resolución, que es `RES_C` entre √12. Calcula `u_c` en °C.
"""),
          cu.ejercicio(h, 3, "u_c", [("tu u_A", "u_A"), ("tu u_B", "u_B")], ["°C"]),
          cu.md("""
### Ejercicio 4 · Incertidumbre expandida (2 pts)
**Para qué sirve:** es el número que se reporta: el intervalo valor ± U contiene al valor verdadero con alrededor
de 95 % de confianza.

Se obtiene multiplicando la combinada por el **factor de cobertura k = 2**. Calcula `U` en °C.
"""),
          cu.ejercicio(h, 4, "U", [("tu u_c", "u_c")], ["°C"]),
          cu.code("""
media = float(np.mean(LECTURAS))
fig, ax = plt.subplots()
ax.plot(range(1, N_LECT + 1), LECTURAS, "o", color="#1F77B4", label="tus lecturas")
ax.axhspan(media - U, media + U, color="#1F77B4", alpha=0.12, label=f"media ± U = {media:.2f} ± {U:.2f} °C")
ax.axhline(T_REF, color="#C62828", ls="--", label=f"referencia {T_REF} °C")
ax.set_xlabel("lectura"); ax.set_ylabel("T (°C)"); ax.legend(loc="upper right", fontsize=8)
titulo(ax, f"{MODELO}: valor ± incertidumbre", alumno)
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### Cierre · ¿Tu registrador es compatible? (1 pt)
Un registrador es **compatible** con la referencia si la diferencia entre su media y la referencia no pasa de su
`U`. Calcula `delta_C` (la media de tus lecturas, impresa arriba, menos `T_REF`) y escribe tu veredicto con los dos números (al menos
20 palabras).
"""),
          cu.code(h("delta_C") + "\n" + h("VEREDICTO") + "\n\n"
                  "completa(delta_C, 'la diferencia con la referencia')\n"
                  "revisa_texto('Veredicto', VEREDICTO, {'la diferencia con la referencia (en valor absoluto)': abs(delta_C),\n"
                  "             'tu incertidumbre expandida U': U})"),
          cu.md("""
## Parte B · Práctica (80 min)
**Objetivo:** aplicar lo mismo a un registro real y decidir si **tu** RC-5 es compatible con los otros dos.

Los tres RC-5 del grupo registraron juntos, en el mismo lugar. A cada alumno le toca uno y una ventana de 60 minutos.
Como no hay termómetro patrón, la **referencia** es la mediana de los otros dos en cada instante.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos | 10 | Cargas la intercomparación y ves los tres registros |
| B2 · Tu ventana | 15 | Separas tu registrador, tu hora y la referencia |
| B3 · Incertidumbre | 25 | Calculas tu u_A, tu U y tu diferencia con la referencia |
| B4 · Conclusión | 20 | Decides si tu registrador es compatible, con tus números |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
tabla, FUENTE = carga_intercomparacion(alumno)
fig, ax = plt.subplots()
for k in tabla.columns[1:4]:
    ax.plot(tabla["minuto"], tabla[k], lw=1, label=k)
ax.set_xlabel("minuto"); ax.set_ylabel("T (°C)"); ax.legend(ncol=3, fontsize=8)
titulo(ax, "Los tres RC-5 juntos", alumno)
firma(fig, alumno); plt.show()
print(f"B1 · {len(tabla)} lecturas por registrador · {tabla['minuto'].iloc[-1]:.0f} min · fuente: {FUENTE}")
"""),
          cu.code("""
MIO, OTROS, INICIO, minuto, T_mio, T_ref = ventana_s4(alumno, tabla)
print(f"B2 · Tu registrador: {MIO} · referencia: mediana de {' y '.join(OTROS)}")
print(f"     Tu ventana: del minuto {INICIO} al {INICIO + VENTANA_MIN} · n = {len(T_mio)} lecturas")
print(f"     Tu RC-5: media = {np.mean(T_mio):.3f} °C · s = {np.std(T_mio, ddof=1):.4f} °C")
print(f"     Referencia: media = {np.mean(T_ref):.3f} °C")
"""),
          cu.md("""
### B3 · Incertidumbre de tu registrador y diferencia con la referencia
Con las fórmulas de la parte A y los números impresos arriba (el RC-5 tiene exactitud ± 0.5 °C y resolución 0.1 °C):
1. `u_A_B`: la incertidumbre tipo A de tu RC-5 (con su *s* y su *n*).
2. `U_B`: la incertidumbre expandida (k = 2), combinando `u_A_B`, la del fabricante y la de la resolución.
3. `delta_B`: la media de tu RC-5 menos la media de la referencia.
"""),
          cu.code(h("u_A_B") + "\n" + h("U_B") + "\n" + h("delta_B") + """

for v, q in ((u_A_B, "u_A_B"), (U_B, "U_B"), (delta_B, "delta_B")):
    completa(v, q)
RESULTADOS = {"u_A": u_A, "u_fab": u_B, "u_c": u_c, "U_exp": U, "delta_C": float(delta_C),
              "u_A_rc5": float(u_A_B), "U_rc5": float(U_B), "delta_rc5": float(delta_B)}
fig, ax = plt.subplots()
ax.plot(minuto, T_ref, color="#888", lw=1.2, label="referencia (mediana de los otros dos)")
ax.fill_between(minuto, T_ref - U_B, T_ref + U_B, color="#888", alpha=0.15, label=f"referencia ± U = ± {U_B:.2f} °C")
ax.plot(minuto, T_mio, color="#D9822B", lw=1.2, label=f"{MIO}")
ax.set_xlabel("minuto"); ax.set_ylabel("T (°C)"); ax.legend(fontsize=8, loc="upper left")
titulo(ax, f"{MIO} contra la referencia", alumno)
firma(fig, alumno, RESULTADOS); plt.show()
print(f"u_A = {u_A_B:.4f} °C · U = {U_B:.3f} °C · diferencia = {delta_B:+.3f} °C → "
      + ("compatible" if abs(delta_B) <= U_B else "no compatible"))
"""),
          cu.md("""
### B4 · Conclusión
¿Tu RC-5 es compatible con la referencia? ¿Qué pesa más en su incertidumbre: el ruido (u_A) o el fabricante? Al
menos 25 palabras, con tu diferencia y tu U.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'tu diferencia con la referencia': abs(delta_B), 'tu U': U_B}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S4_<código>.csv`. En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar →
Subir** → elige el archivo → **Reemplazar la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
ruta = f"S4_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"minuto": minuto, "T_mio_C": T_mio, "T_referencia_C": T_ref},
             extra={"fuente": FUENTE, "registrador": MIO, "ventana": f"minuto {INICIO} a {INICIO + VENTANA_MIN}"})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
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
1. Pega en `CODIGOS` la lista de códigos del grupo y ejecuta: la tabla da los resultados esperados de la parte A y
   de la parte B (con la intercomparación cargada). Tolerancia sugerida: 2 %.
2. Sube los CSV entregados (ícono de carpeta) y ejecuta la última celda.
"""),
              cu.code('''
import pandas as pd, glob
CODIGOS = """
217654321
219876543
""".split()

def clave_completa(c):
    a = identificar("Alumno Clave", c, SESION)
    k = clave_s4(a)
    mio, _, ini, _, t_mio, t_ref = ventana_s4(a, tabla)
    u_a = np.std(t_mio, ddof=1) / np.sqrt(len(t_mio))
    k.update({"u_A_rc5": u_a, "U_rc5": 2 * np.sqrt(u_a ** 2 + (EXACT_RC5_C / np.sqrt(3)) ** 2 + (RES_RC5_C / np.sqrt(12)) ** 2),
              "delta_rc5": float(np.mean(t_mio) - np.mean(t_ref))})
    return mio, ini, k

filas = []
for c in CODIGOS:
    mio, ini, k = clave_completa(c)
    filas.append({"codigo": c, "registrador": mio, "inicio_min": ini, **{x: round(float(v), 4) for x, v in k.items()}})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
for ruta in sorted(glob.glob("S4_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    _, _, k = clave_completa(meta["codigo"])
    malos = [x for x in k if x not in res or abs(res[x] - k[x]) > 0.02 * max(abs(k[x]), 1e-3)]
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · "
          f"fuente {meta.get('fuente')} · " + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("u_A", "★ Incertidumbre tipo A, parte A (°C)", "0.0000"),
                    ("u_fab", "Incertidumbre tipo B del fabricante (°C)", "0.0000"),
                    ("u_c", "Incertidumbre combinada (°C)", "0.0000"),
                    ("U_exp", "Incertidumbre expandida, k = 2 (°C)", "0.000"),
                    ("delta_C", "Diferencia con la referencia, parte A (°C)", "0.000"),
                    ("u_A_rc5", "Incertidumbre tipo A de tu RC-5 (°C)", "0.0000"),
                    ("U_rc5", "Incertidumbre expandida de tu RC-5 (°C)", "0.000"),
                    ("delta_rc5", "Diferencia de tu RC-5 con la referencia (°C)", "0.000")],
        comparacion=("U_rc5", "delta_rc5", "¿Tu RC-5 es compatible con la referencia? (|diferencia| ≤ U)", "dentro"),
        preguntas=["1. ¿Qué pesa más en la incertidumbre de tu RC-5, el ruido de las lecturas o la exactitud del "
                   "fabricante? Usa tus números.",
                   "2. Si tu RC-5 no fuera compatible, ¿qué harías antes de usarlo en una auditoría?"],
        tabla={"encabezado_csv": "minuto", "x": ("A", "Minuto"),
               "series": [("B", "Tu RC-5"), ("C", "Referencia")]},
        grafica={"titulo": "Tu RC-5 contra la referencia", "x": "Minuto", "y": "Temperatura (°C)",
                 "tipo": "dispersion"},
        renglones=400,
        metadatos=(("Fuente de los datos", "fuente"), ("Registrador", "registrador"), ("Ventana", "ventana")),
        csv_ejemplo=csv_ejemplo)


if __name__ == "__main__":
    cu.guardar(celdas(), ALUMNO)
    cu.guardar(celdas(prof=True), PROF)
    generar_hoja()
    print("listo:", ALUMNO, PROF, HOJA, sep="\n  ")
    if len(sys.argv) == 3 and sys.argv[1] == "--prueba":
        cu.guardar(celdas(r="numero", nombre="Alumno De Prueba", codigo="217654321"),
                   os.path.join(sys.argv[2], f"{SESION}_numeros.ipynb"))
        ruta = cu.guardar(celdas(r=True, nombre="Alumno De Prueba", codigo="217654321"),
                          os.path.join(sys.argv[2], "S4_resuelto.ipynb"))
        print("  prueba:", ruta)
