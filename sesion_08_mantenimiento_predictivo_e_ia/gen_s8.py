"""Sesión 8 · Mantenimiento predictivo e IA. Genera:

    S8_AC_CLASE_Colab_ALUMNO.ipynb               (repositorio)
    S8_AC_CLASE_Colab_PROF.ipynb                 (sólo Drive: soluciones, clave del grupo y verificación de CSV)
    S8_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx   (repositorio y Drive)

Uso:  python gen_s8.py            -> los tres archivos
      python gen_s8.py --prueba D -> además, una versión resuelta en D para ejecutarla

Parte A: una bomba con su indicador de salud (velocidad de vibración) y una flota con su matriz de confusión y sus
costos, por código. Parte B: C-MAPSS FD001 de la NASA (datos/): 100 motores hasta la falla; el código asigna un motor
y el ciclo «de hoy»; vida remanente lineal contra exponencial contra real; umbral de alarma por costo; un modelo de
aprendizaje automático (regresión logística con 10 sensores) contra el umbral, en 100 motores que no vio.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "comun"))
import cuaderno as cu  # noqa: E402
import hoja  # noqa: E402

SESION = "S8"
CARPETA = "sesion_08_mantenimiento_predictivo_e_ia"
ALUMNO = os.path.join(AQUI, "S8_AC_CLASE_Colab_ALUMNO.ipynb")
PROF = os.path.join(AQUI, "S8_AC_CLASE_Colab_PROF.ipynb")
HOJA = os.path.join(AQUI, "S8_AC_PRACT_Hoja_de_resultados_ALUMNO.xlsx")
COLAB = cu.REPO + CARPETA + "/S8_AC_CLASE_Colab_ALUMNO.ipynb"
RAMA = os.environ.get("DAQ_RAMA", "main")   # para probar una rama antes de aceptarla; los cuadernos publicados usan main
URL_DATOS = f"https://raw.githubusercontent.com/ggt13/DAQ_TSU/{RAMA}/{CARPETA}/datos/"

DATOS_S8 = f'URL_DATOS = "{URL_DATOS}"\n' + r'''
import warnings
import pandas as pd
from scipy.optimize import curve_fit

MAQUINAS_A = ["Bomba de agua helada del chiller 2", "Bomba de la torre de enfriamiento", "Bomba de agua de proceso",
              "Bomba de condensados", "Bomba del sistema contra incendio (prueba semanal)"]
U_A = 4.5                         # mm/s: límite entre las zonas C y D de ISO 10816-3 (sesión 7)
COLUMNAS = ["unidad", "ciclo", "op1", "op2", "op3"] + [f"s{i}" for i in range(1, 22)]
SENSORES = ["s2", "s3", "s4", "s7", "s11", "s12", "s15", "s17", "s20", "s21"]   # 10 de los 14 que cambian con el desgaste
HORIZONTE = 30                    # «falla pronto»: le quedan 30 ciclos o menos
SUAVE = 10                        # promedio móvil de 10 ciclos (sesión 5)
C_INT_B = 50                      # miles de pesos por revisión planeada (parte B); la falla depende del código
COSTOS_FALLA_B = [100, 150, 200, 500, 750, 1000]
MOMENTOS = 10                     # momentos de decisión por motor de entrenamiento, elegidos al azar con semilla fija
M_MIN_B = 0.002                   # psia por ciclo: con una pendiente menor la recta no dice nada
UMBRALES_B = np.round(np.arange(47.60, 48.101, 0.05), 2)


def datos_s8(alumno):
    """Parte A: la bomba y su indicador de salud; la flota con su matriz de confusión y sus costos."""
    hi = parametro(alumno, "hi", 1.8, 3.6, 2)
    m = parametro(alumno, "m", 0.010, 0.060, 4)
    n = asignar(alumno, [30, 40, 50, 60], salto=1)
    p = int(round(n * parametro(alumno, "p", 0.15, 0.35, 3)))
    vp = int(round(p * parametro(alumno, "sens", 0.6, 0.95, 3)))
    fp = int(round((n - p) * parametro(alumno, "fpr", 0.05, 0.6, 3)))
    return dict(MAQUINA=asignar(alumno, MAQUINAS_A, salto=2), HI_HOY=hi, M_A=m, N_FLOTA=n,
                VP=vp, FN=p - vp, FP=fp, VN=n - p - fp,
                C_INT=int(round(parametro(alumno, "c_int", 15, 60, 0))),
                C_FALLA=int(round(parametro(alumno, "c_falla", 60, 250, 0))))


def clave_s8(alumno):
    d = datos_s8(alumno)
    return {"rul_A": (U_A - d["HI_HOY"]) / d["M_A"], "precision_A": d["VP"] / (d["VP"] + d["FP"]),
            "sens_A": d["VP"] / (d["VP"] + d["FN"]),
            "costo_pred_A": (d["VP"] + d["FP"]) * d["C_INT"] + d["FN"] * d["C_FALLA"]}


def _lee(nombre):
    """Lee un archivo de C-MAPSS del repositorio o, si se subió, de la carpeta de Colab."""
    errores = []
    for origen in (URL_DATOS + nombre, nombre):
        try:
            return pd.read_csv(origen, sep=r"\s+", header=None, compression="gzip")
        except Exception as e:
            errores.append(f"{origen}: {type(e).__name__} {e}"[:160])
    raise OSError(" | ".join(errores))


def carga_cmapss(alumno):
    """Entrenamiento, prueba y vida remanente real de la prueba. Si no se pueden leer, sintéticos marcados."""
    try:
        train, test = _lee("train_FD001.txt.gz"), _lee("test_FD001.txt.gz")
        rul = _lee("RUL_FD001.txt.gz")[0].to_numpy()
        train.columns = test.columns = COLUMNAS
        return train, test, rul, "C-MAPSS FD001, NASA Prognostics Center of Excellence"
    except Exception as e:
        print(f"⚠ No se pudieron leer los datos de C-MAPSS: {e}")
        print("⚠ Sube los tres archivos .txt.gz con el ícono de carpeta y vuelve a ejecutar. Mientras tanto, SINTÉTICOS.")
    g = np.random.default_rng(2027)
    filas_tr, filas_te, rul = [], [], []
    for u in range(1, 201):
        vida = int(g.integers(130, 360))
        t = np.arange(1, vida + 1)
        dano = np.exp(4 * (t / vida - 1))
        x = {f"s{i}": 100 + g.normal(0, 0.2, vida) for i in range(1, 22)}
        for k, s in enumerate(SENSORES):
            x[s] = 100 + (1 if k % 2 else -1) * 0.8 * dano + g.normal(0, 0.15, vida)
        x["s11"] = 47.3 + 0.8 * dano + g.normal(0, 0.15, vida)
        tabla = pd.DataFrame({"unidad": (u - 1) % 100 + 1, "ciclo": t, "op1": 0.0, "op2": 0.0, "op3": 100.0, **x})
        if u <= 100:
            filas_tr.append(tabla)
        else:
            corte = int(g.integers(int(0.4 * vida), vida - 5))
            filas_te.append(tabla.iloc[:corte])
            rul.append(vida - corte)
    return (pd.concat(filas_tr, ignore_index=True)[COLUMNAS], pd.concat(filas_te, ignore_index=True)[COLUMNAS],
            np.array(rul), "SINTÉTICOS (sin los datos de C-MAPSS)")


def suaviza(tabla):
    """Promedio móvil de 10 ciclos de cada sensor, motor por motor; HI es la s11 suavizada."""
    t = tabla.copy()
    t[SENSORES] = t.groupby("unidad")[SENSORES].transform(lambda x: x.rolling(SUAVE, min_periods=1).mean())
    t["HI"] = t["s11"]
    return t


def prepara_train(train):
    t = suaviza(train)
    t["vida"] = t.groupby("unidad").ciclo.transform("max")
    t["RUL"] = t.vida - t.ciclo
    return t


def umbral_falla(tr):
    """Umbral de falla del indicador: media − desviación estándar de su valor en el último ciclo de cada motor.

    Es un nivel conservador: lo alcanzan casi 9 de cada 10 motores antes de fallar."""
    fin = tr[tr.RUL == 0].HI
    return round(float(fin.mean() - fin.std()), 2)


def caso_b(alumno, tr):
    """Tu motor y tu «hoy»: entre el 72 y el 85 % de su vida, con tendencia clara en los últimos 30 ciclos.

    Sólo se asignan motores cuyo indicador sí llega al umbral de falla."""
    U = umbral_falla(tr)
    fin = tr[tr.RUL == 0]
    u = asignar(alumno, sorted(fin[fin.HI >= U].unidad))
    g = tr[tr.unidad == u]
    vida = int(g.vida.iloc[0])
    c = int(parametro(alumno, "frac_b", 0.72, 0.85, 3) * vida)
    while True:
        h = g[(g.ciclo <= c) & (g.ciclo > c - 30)]
        m, b = np.polyfit(h.ciclo, h.HI, 1)
        if m >= M_MIN_B or c >= vida - 10:
            break
        c += 5
    return dict(UNIDAD=int(u), VIDA=vida, CICLO_HOY=c, HI_HOY_B=round(float(m * c + b), 3), M_B=round(float(m), 5),
                RUL_REAL=vida - c)


def _expo(t, a, c, k):
    return a + c * np.exp(k * t / 100)


def rul_exponencial(g, c, U):
    """Ajusta HI = a + c·exp(k·t/100) a todo lo conocido hasta el ciclo c y calcula cuándo llega a U."""
    h = g[g.ciclo <= c]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            (a, cc, k), _ = curve_fit(_expo, h.ciclo, h.HI, p0=(47.3, 0.05, 1.5), maxfev=20000,
                                      bounds=([46, 1e-6, 1e-3], [48.5, 10, 10]))
        except Exception:
            return float("nan"), None
    if U <= a or cc <= 0 or k <= 0:
        return float("nan"), None
    return float(100 / k * np.log((U - a) / cc) - c), (a, cc, k)


def momentos(tr):
    """10 momentos de decisión al azar en la vida de cada motor de entrenamiento (1000 en total, semilla fija)."""
    g = np.random.default_rng(2027)
    idx = np.concatenate([g.choice(ix, MOMENTOS, replace=False) for _, ix in sorted(tr.groupby("unidad").groups.items())])
    return tr.loc[idx]


def costo(vp, fp, fn, c_falla):
    return (vp + fp) * C_INT_B + fn * c_falla


def tabla_umbrales(mom, c_falla):
    """Para cada umbral del HI: matriz de confusión de «falla en 30 ciclos o menos» en los momentos de decisión."""
    y = mom.RUL <= HORIZONTE
    filas = []
    for u in UMBRALES_B:
        p = mom.HI > u
        vp, fp, fn = int((p & y).sum()), int((p & ~y).sum()), int((~p & y).sum())
        filas.append({"umbral": u, "VP": vp, "FP": fp, "FN": fn,
                      "precision": vp / (vp + fp) if vp + fp else float("nan"), "sensibilidad": vp / (vp + fn),
                      "costo": costo(vp, fp, fn, c_falla)})
    return pd.DataFrame(filas)


def corte_ia(modelo, mom, c_falla):
    """El corte de probabilidad de la IA que menos cuesta en los momentos de entrenamiento: misma regla que el umbral."""
    y = (mom.RUL <= HORIZONTE).to_numpy()
    pr = modelo.predict_proba(mom[SENSORES])[:, 1]
    def c(q):
        m = matriz(pr > q, y)
        return costo(m["VP"], m["FP"], m["FN"], c_falla)
    return float(min(np.round(np.arange(0.05, 0.951, 0.05), 2), key=c))


def arbol_sin_limite(tr, ult, real):
    """Árbol de decisión sin límite de profundidad: sensibilidad en entrenamiento y en prueba (sobreajuste)."""
    from sklearn.tree import DecisionTreeClassifier
    y = tr.RUL <= HORIZONTE
    a = DecisionTreeClassifier(random_state=0).fit(tr[SENSORES], y)
    s_tr = matriz(a.predict(tr[SENSORES]), y)
    s_te = matriz(a.predict(ult[SENSORES]), real)
    return s_tr["VP"] / (s_tr["VP"] + s_tr["FN"]), s_te["VP"] / (s_te["VP"] + s_te["FN"])


def ultimo_ciclo(test):
    """El último ciclo registrado de cada motor de prueba, ya suavizado."""
    return suaviza(test).groupby("unidad").tail(1).reset_index(drop=True)


def matriz(pred, real):
    pred, real = np.asarray(pred, bool), np.asarray(real, bool)
    return dict(VP=int((pred & real).sum()), FP=int((pred & ~real).sum()), FN=int((~pred & real).sum()),
                VN=int((~pred & ~real).sum()))


def modelo_ia(tr):
    """Regresión logística con los 10 sensores suavizados: probabilidad de que el motor falle en 30 ciclos o menos."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    m = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000))
    m.fit(tr[SENSORES], tr.RUL <= HORIZONTE)
    return m


def revisa_umbral(u):
    if u is None:
        raise ValueError("Escribe UMBRAL_ALARMA, el umbral que elegiste de la tabla.")
    if not np.isclose(UMBRALES_B, float(u)).any():
        raise ValueError("Umbral de alarma: escribe uno de los valores de la tabla: "
                         + ", ".join(f"{v:.2f}" for v in UMBRALES_B) + ".")
    REGISTRO["Umbral de alarma"] = True
    print(f"✔ Umbral de alarma: {float(u):.2f} psia")
'''

SOL = {
    "rul_A": "(U_A - HI_HOY) / M_A",
    "SUST_1": 'f"({U_A} − {HI_HOY}) mm/s / {M_A} mm/s por día = {rul_A:.4g} días"',
    "PRED_1": '"si el desgaste sigue igual la bomba llega a la zona D en ese tiempo y la reparación se programa antes"',
    "precision_A": "VP / (VP + FP)",
    "SUST_2": 'f"{VP} / ({VP} + {FP}) = {precision_A:.4g} (adimensional)"',
    "PRED_2": '"de cada alarma esta fracción era una falla de verdad y el resto fueron revisiones que no hacían falta"',
    "sens_A": "VP / (VP + FN)",
    "SUST_3": 'f"{VP} / ({VP} + {FN}) = {sens_A:.4g} (adimensional)"',
    "PRED_3": '"de las bombas que sí iban a fallar esta fracción se detectó a tiempo y las demás fallaron en operación"',
    "costo_pred_A": "(VP + FP) * C_INT + FN * C_FALLA",
    "SUST_4": 'f"({VP} + {FP}) × {C_INT} + {FN} × {C_FALLA} = {costo_pred_A:.0f} miles de pesos"',
    "PRED_4": '"el predictivo cuesta las revisiones que manda más las fallas que no detecta y se compara con dejar que fallen"',
    "CIERRE": ('f"Con el predictivo la flota costó {costo_pred_A:.0f} miles de pesos y dejando fallar todo {COSTO_CORR_A:.0f}; '
               '{\'conviene el predictivo\' if costo_pred_A < COSTO_CORR_A else \'no conviene el predictivo\'} aunque '
               'su precisión sea {precision_A:.2f}"'),
    "RUL_PRED_B": "(U_B - HI_HOY_B) / M_B",
    "UMBRAL_ALARMA": "float(TABLA.loc[TABLA.costo.idxmin(), 'umbral'])",
    "SENS_PRUEBA": "M_UMB['VP'] / (M_UMB['VP'] + M_UMB['FN'])",
    "CONCLUSION_B": ('f"La recta predijo {RUL_PRED_B:.4g} ciclos y al motor le quedaban {RUL_REAL} ciclos, porque el '
                     'desgaste se acelera. En prueba mi umbral detectó una fracción {SENS_PRUEBA:.2f} de los motores por '
                     'fallar y el modelo de IA {SENS_IA:.2f}; con 25 motores esa diferencia no basta para preferir uno"'),
}


def celdas(r=False, prof=False, nombre="", codigo=""):
    h = cu.Huecos(SOL, r if r else prof)
    C = [cu.md(f"""
# S8 · Mantenimiento predictivo e IA · ¿Cuánto le queda y cuándo intervenir?
**Sistemas de adquisición de datos · TSU en Electrónica y Pruebas · Jabil**

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]({COLAB})

## Objetivo
Estimar la **vida remanente** (RUL, *remaining useful life*) de una máquina con la tendencia de un **indicador de
salud**, y decidir **cuándo** dar la alarma con la **matriz de confusión** y el **costo** de cada error. Comparar una
regla sencilla (un umbral) con un modelo de **aprendizaje automático** que combina varios sensores, en máquinas que
el modelo no vio. Es el mantenimiento **predictivo**: se interviene antes de la falla, no por calendario ni después.

## La situación
En la sesión 7 la vibración dijo **qué** falla; ahora hay que decir **cuándo**. En clase trabajas con **tu** bomba (su
indicador de salud y su tendencia) y con una flota de bombas vigiladas por una regla de alarma. En la práctica usas
datos de la NASA: 100 motores turbofan simulados que operan desde nuevos hasta fallar por desgaste del compresor, con
21 sensores; tu motor y tu «hoy» dependen de tu código.

## En qué consiste este cuaderno
| Parte | Tiempo | Qué haces | Qué produce |
|---|---|---|---|
| **A · Actividad en clase** | 30 min | Cuatro ejercicios (★ primero): la vida remanente de tu bomba, la precisión y la sensibilidad de la alarma de la flota, y su costo. En cada uno escribes tu resultado, la sustitución con tus números y su unidad, y lo que predice | La fecha de tu intervención y si la alarma conviene |
| **B · Práctica** | 80 min | Predices la vida remanente de tu motor con una recta y la comparas con la real y con una curva; eliges un umbral por costo; comparas el umbral con un modelo de IA en 100 motores nuevos | Gráficas firmadas, tu conclusión y el archivo `S8_<código>.csv` |
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
         cu.herramientas(DATOS_S8)]
    C += cu.identificacion(SESION, nombre, codigo)
    C += [cu.md("""
## Parte A · Actividad en clase (30 min)
Ejecuta la celda para ver **tu** bomba y **tu** flota. El **indicador de salud** de la bomba es su velocidad de
vibración RMS (sesión 7); la reparación debe hacerse antes de que llegue a **4.5 mm/s**, el límite de la zona D.

La flota tiene una **regla de alarma**. Cada bomba cae en una de cuatro casillas de la **matriz de confusión**:

| | Sí iba a fallar | No iba a fallar |
|---|---|---|
| **La alarma sonó** | VP: verdadero positivo | FP: falso positivo (revisión de más) |
| **No sonó** | FN: falso negativo (falla en operación) | VN: verdadero negativo |

**Cómo se llena cada ejercicio.** Ejemplo con otros datos (no son los tuyos):
```
rul_A  = 50.0
SUST_1 = "(4.5 − 3.0) mm/s / 0.03 mm/s por día = 50.0 días"
PRED_1 = "si el desgaste sigue igual la bomba llega al límite en unos cincuenta días"
```
Precisión y sensibilidad son fracciones entre 0 y 1 (no en %) y no tienen unidad: escribe «(adimensional)» o «sin
unidad» después del resultado.
"""),
          cu.code("""
globals().update(datos_s8(alumno))
print(f"Tu bomba · {MAQUINA}")
print(f"  Indicador de salud hoy: HI_HOY = {HI_HOY} mm/s · tendencia de los últimos 30 días: M_A = {M_A} mm/s por día · "
      f"límite U_A = {U_A} mm/s")
print(f"\\nTu flota de N_FLOTA = {N_FLOTA} bombas, un año con la regla de alarma:")
print(f"  VP = {VP} · FP = {FP} · FN = {FN} · VN = {VN}")
print(f"  Costo de una revisión planeada: C_INT = {C_INT} miles de pesos · de una falla en operación: C_FALLA = {C_FALLA} miles de pesos")
"""),
          cu.md("""
### ★ Ejercicio 1 · ¿Cuánto le queda a tu bomba? (3 pts)
**Para qué sirve:** es el número con el que se programa la reparación: refacciones, personal y paro planeado.

Si la tendencia sigue igual: **RUL = (U − HI_hoy) / m**. Calcula `rul_A` en días.
"""),
          cu.ejercicio(h, 1, "rul_A", [("tu indicador de hoy", "HI_HOY"), ("tu tendencia", "M_A"), ("el límite", "U_A")],
                       ["día", "dia", "Día", "Dia", "DÍA"]),
          cu.md("""
### Ejercicio 2 · ¿Cuántas alarmas eran ciertas? Precisión (2 pts)
**Para qué sirve:** si la precisión es baja, el personal deja de creerle a la alarma.

**Precisión = VP / (VP + FP)**: de todas las veces que sonó, la fracción que era una falla real.
"""),
          cu.ejercicio(h, 2, "precision_A", ["VP", "FP"], ["adimensional", "Adimensional", "sin unidad", "Sin unidad"]),
          cu.md("""
### Ejercicio 3 · ¿Cuántas fallas detectó? Sensibilidad (2 pts)
**Para qué sirve:** cada falla no detectada es un paro no planeado.

**Sensibilidad = VP / (VP + FN)**: de las bombas que sí iban a fallar, la fracción en que sonó la alarma.
"""),
          cu.ejercicio(h, 3, "sens_A", ["VP", "FN"], ["adimensional", "Adimensional", "sin unidad", "Sin unidad"]),
          cu.md("""
### Ejercicio 4 · ¿Cuánto costó el año con la alarma? (2 pts)
**Para qué sirve:** la decisión se toma en pesos: revisar de más cuesta poco, una falla en operación cuesta mucho.

Cada alarma (VP o FP) cuesta una revisión planeada; cada falla no detectada (FN) cuesta una falla en operación:
**costo = (VP + FP) · C_INT + FN · C_FALLA**. Resultado en miles de pesos.
"""),
          cu.ejercicio(h, 4, "costo_pred_A", ["VP", "FP", "FN", ("tu costo de revisión", "C_INT"),
                                              ("tu costo de falla", "C_FALLA")],
                       ["miles de pesos", "mil pesos", "Miles de pesos", "pesos", "k$", "MXN"]),
          cu.code("""
COSTO_CORR_A = (VP + FN) * C_FALLA
COSTO_PREV_A = N_FLOTA * C_INT                    # preventivo: revisar todas las bombas cada año
dias = np.arange(-30, int(rul_A) + 10)
fig, ax = plt.subplots()
ax.plot(dias[dias <= 0], HI_HOY + M_A * dias[dias <= 0] + alumno.rng("hi").normal(0, 0.04, (dias <= 0).sum()), "o",
        ms=3, color="#1F5FAD", label="indicador medido")
ax.plot(dias[dias >= 0], HI_HOY + M_A * dias[dias >= 0], "--", color="#D9822B", label=f"tendencia: llega en {rul_A:.0f} días")
ax.axhline(U_A, color="#C62828", lw=1, label=f"límite {U_A} mm/s"); ax.axvline(0, color="#888", lw=0.8)
ax.set_xlabel("días desde hoy"); ax.set_ylabel("velocidad RMS (mm/s)"); ax.legend(fontsize=8)
titulo(ax, "Vida remanente de tu bomba", alumno)
firma(fig, alumno); plt.show()
print(f"Mantenimiento correctivo (dejar fallar las {VP + FN} bombas que fallan): {COSTO_CORR_A} miles de pesos")
print(f"Mantenimiento preventivo (revisar las {N_FLOTA} bombas, suponiendo que la revisión evita todas las fallas): "
      f"{COSTO_PREV_A} miles de pesos")
print(f"Mantenimiento predictivo con la alarma: {costo_pred_A:.0f} miles de pesos")
"""),
          cu.md("""
### Cierre (1 pt)
¿Conviene la alarma frente a dejar fallar las bombas? Compara los costos impresos arriba (también el del preventivo)
y di qué importa más en tu flota, la precisión o la sensibilidad. Al menos 20 palabras, con los costos del
predictivo y del correctivo.
"""),
          cu.code(h("CIERRE") + "\n\nrevisa_texto('Cierre', CIERRE, {'el costo con predictivo': costo_pred_A,\n"
                  "             'el costo correctivo': COSTO_CORR_A})"),
          cu.md(f"""
## Parte B · Práctica (80 min)
**Objetivo:** con datos de degradación hasta la falla, ver cuándo funciona una predicción sencilla y cuándo hace falta
un modelo, y medir los dos en máquinas nuevas.

**C-MAPSS FD001** (NASA): 100 motores de entrenamiento que operan desde nuevos hasta fallar y 100 de prueba cuyo
registro termina antes de la falla (se sabe cuánto les quedaba). Un ciclo es un vuelo. El indicador de salud es el
sensor **s11**, la presión a la salida del compresor de alta (psia), suavizado con un promedio móvil de 10 ciclos
(sesión 5). El **umbral de falla** `U_B` es el promedio del indicador en el último ciclo de los 100 motores menos una
desviación estándar: un nivel conservador que casi 9 de cada 10 motores alcanzan antes de fallar. Son datos simulados con un modelo físico del motor y ruido de sensor; se usan en todo el mundo para
probar métodos de pronóstico.

| Bloque | min | Qué haces |
|---|---|---|
| B1 · Datos y tu motor | 10 | Ves la flota y tu motor hasta tu «hoy» |
| B2 · Vida remanente con una recta | 15 | Calculas a mano cuántos ciclos le quedan y lo comparas con lo real |
| B3 · Umbral por costo | 15 | Eliges el umbral de alarma que menos cuesta en el entrenamiento, con tu costo de falla |
| B4 · Umbral contra IA en motores nuevos | 20 | Matriz de confusión de tu umbral y de un modelo de IA en los 100 motores de prueba; un modelo que memoriza |
| B5 · Conclusión | 10 | Con tus números, y qué hace falta para usar IA en planta |
| Tabla y captura | 10 | Descargas el CSV y lo importas en tu hoja de resultados |
"""),
          cu.code("""
if "TRAIN" not in globals() or FUENTE.startswith("SINTÉTICOS"):
    TRAIN, TEST, RUL_TEST, FUENTE = carga_cmapss(alumno)
TR = prepara_train(TRAIN)
U_B = umbral_falla(TR)
globals().update(caso_b(alumno, TR))
G = TR[TR.unidad == UNIDAD]
print(f"B1 · Fuente: {FUENTE}")
print(f"     Entrenamiento: {TR.unidad.nunique()} motores, vida de {TR.vida.min()} a {TR.vida.max()} ciclos · "
      f"umbral de falla del indicador: U_B = {U_B} psia (último ciclo de la flota: media − desviación)")
C_FALLA_B = asignar(alumno, COSTOS_FALLA_B, salto=3)
print(f"     Tu motor: {UNIDAD} · tu «hoy»: ciclo {CICLO_HOY} · tu costo de una falla en operación: C_FALLA_B = "
      f"{C_FALLA_B} miles de pesos (revisión planeada: {C_INT_B})")
fig, ax = plt.subplots(figsize=(10, 4))
for u, g in TR.groupby("unidad"):
    ax.plot(g.ciclo, g.HI, color="#DDDDDD", lw=0.5)
ax.plot(G.ciclo[G.ciclo <= CICLO_HOY], G.HI[G.ciclo <= CICLO_HOY], color="#1F5FAD", lw=2, label=f"tu motor {UNIDAD} hasta hoy")
ax.axhline(U_B, color="#C62828", lw=1, label=f"umbral de falla {U_B}")
ax.set_xlabel("ciclo"); ax.set_ylabel("s11 suavizada (psia)"); ax.legend(fontsize=8)
titulo(ax, "Indicador de salud de la flota", alumno)
firma(fig, alumno); plt.show()
"""),
          cu.md("""
### B2 · Vida remanente con una recta
El cuaderno ajusta una recta a los últimos 30 ciclos de tu motor (`M_B`, en psia por ciclo) y da el valor de hoy en
esa recta (`HI_HOY_B`). Con la fórmula del ★ calcula `RUL_PRED_B`, en ciclos. Después verás cuántos le quedaban
de verdad y qué predice una curva exponencial ajustada a toda su historia.
"""),
          cu.code('print(f"HI_HOY_B = {HI_HOY_B:.3f} psia · M_B = {M_B:.5f} psia por ciclo · U_B = {U_B:.2f} psia")'),
          cu.code(h("RUL_PRED_B", "✎ tu vida remanente predicha, en ciclos") + """

completa(RUL_PRED_B, "tu vida remanente predicha")
RUL_EXP, par = rul_exponencial(G, CICLO_HOY, U_B)
t_fut = np.arange(CICLO_HOY - 30, max(VIDA, CICLO_HOY + min(RUL_PRED_B, 2 * VIDA)) + 10)
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(G.ciclo[G.ciclo <= CICLO_HOY], G.HI[G.ciclo <= CICLO_HOY], color="#1F5FAD", lw=1.5, label="lo que se sabía hoy")
ax.plot(G.ciclo[G.ciclo > CICLO_HOY], G.HI[G.ciclo > CICLO_HOY], color="#9DB7D5", lw=1.5, label="lo que pasó después")
ax.plot(t_fut, HI_HOY_B + M_B * (t_fut - CICLO_HOY), "--", color="#D9822B", label=f"recta: {RUL_PRED_B:.0f} ciclos")
if par is not None:
    ax.plot(t_fut, par[0] + par[1] * np.exp(par[2] * t_fut / 100), ":", color="#6A1B9A", lw=2,
            label=f"exponencial: {RUL_EXP:.0f} ciclos")
ax.axhline(U_B, color="#C62828", lw=1); ax.axvline(CICLO_HOY, color="#888", lw=0.8)
ax.axvline(VIDA, color="#C62828", ls=":", lw=1, label=f"falla real: {RUL_REAL} ciclos después de hoy")
ax.set_ylim(G.HI.min() - 0.05, U_B + 0.25); ax.set_xlabel("ciclo"); ax.set_ylabel("s11 suavizada (psia)")
ax.legend(fontsize=8, loc="upper left"); titulo(ax, f"Vida remanente del motor {UNIDAD}", alumno)
firma(fig, alumno); plt.show()
print(f"Recta: {RUL_PRED_B:.0f} ciclos · exponencial: " + ("no se pudo ajustar" if np.isnan(RUL_EXP) else f"{RUL_EXP:.0f} ciclos")
      + f" · real: {RUL_REAL} ciclos")
print("El desgaste se acelera: la recta supone que sigue al ritmo de hoy. En 9 de cada 10 casos de esta flota promete "
      "más vida de la que hay; la exponencial queda más cerca en casi 8 de cada 10.")
"""),
          cu.md("""
### B3 · Umbral de alarma por costo
La regla: **alarma si el indicador pasa un umbral**. Para elegirlo se simulan 1000 decisiones: 10 momentos al azar
en la vida de cada motor de entrenamiento, en los que se sabe si al motor le quedaban 30 ciclos o menos. La tabla da,
para cada umbral, la matriz de confusión, la precisión, la sensibilidad y el costo con **tu** costo de falla. Un umbral
bajo da muchas alarmas falsas (aunque muchas son **tempranas**: motores con 31 a 50 ciclos); uno alto deja pasar
fallas. **Elige el de menor costo** y escríbelo en `UMBRAL_ALARMA`.
"""),
          cu.code("""
MOM = momentos(TR)
TABLA = tabla_umbrales(MOM, C_FALLA_B)
print(f"Umbral en psia · VP, FP y FN en 1000 decisiones · costo en miles de pesos con revisión {C_INT_B} y falla {C_FALLA_B}")
print(TABLA.to_string(index=False, formatters={"umbral": "{:.2f}".format, "precision": "{:.2f}".format,
                                               "sensibilidad": "{:.2f}".format, "costo": "{:,.0f}".format}))
"""),
          cu.code(h("UMBRAL_ALARMA", "✎ el umbral que elegiste, en psia", vacio="None") + """

revisa_umbral(UMBRAL_ALARMA)
UMBRAL_ALARMA = float(UMBRAL_ALARMA)
"""),
          cu.md("""
### B4 · Tu umbral contra un modelo de IA, en 100 motores que no se usaron para ajustar nada
El modelo de **aprendizaje automático** (regresión logística) aprendió del entrenamiento a combinar **10 sensores**,
no sólo s11, y da una probabilidad de falla; su corte de alarma se eligió con **tu mismo costo** y las mismas 1000
decisiones que tu umbral, para que la comparación sea justa. Los dos se prueban en el último ciclo de los 100 motores
de prueba: ¿les quedaban 30 ciclos o menos? Sólo 25 de ellos fallaban pronto, así que **un motor cambia la
sensibilidad en 0.04**: diferencias de ese tamaño no distinguen los dos métodos. Con la matriz de **tu umbral**
calcula la sensibilidad en prueba, `SENS_PRUEBA` (entre 0 y 1).

Al final, un **árbol de decisión sin límite** muestra el riesgo de la IA: memoriza el entrenamiento y le va peor en
motores que no vio (**sobreajuste**). Por eso un modelo se evalúa siempre en máquinas **distintas** de las que usó
para aprender; si se mezclan ciclos del mismo motor en entrenamiento y prueba, el resultado sale engañosamente bueno
(**fuga de datos**).
"""),
          cu.code("""
ULT = ultimo_ciclo(TEST)
REAL_PRUEBA = RUL_TEST <= HORIZONTE
M_UMB = matriz(ULT.HI > UMBRAL_ALARMA, REAL_PRUEBA)
IA = modelo_ia(TR)
Q_IA = corte_ia(IA, MOM, C_FALLA_B)
M_IA = matriz(IA.predict_proba(ULT[SENSORES])[:, 1] > Q_IA, REAL_PRUEBA)
SENS_IA = M_IA["VP"] / (M_IA["VP"] + M_IA["FN"])
PREC_IA = M_IA["VP"] / max(1, M_IA["VP"] + M_IA["FP"])
print(f"100 motores de prueba · {int(REAL_PRUEBA.sum())} de ellos fallaban en 30 ciclos o menos")
print(f"Tu umbral ({UMBRAL_ALARMA:.2f} psia):  VP = {M_UMB['VP']} · FP = {M_UMB['FP']} · FN = {M_UMB['FN']} · VN = {M_UMB['VN']}")
print(f"Modelo de IA (10 sensores, corte {Q_IA:.2f}): VP = {M_IA['VP']} · FP = {M_IA['FP']} · FN = {M_IA['FN']} · "
      f"VN = {M_IA['VN']} · sensibilidad {SENS_IA:.2f} · precisión {PREC_IA:.2f}")
"""),
          cu.code(h("SENS_PRUEBA", "✎ la sensibilidad de tu umbral en prueba") + """

completa(SENS_PRUEBA, "la sensibilidad de tu umbral")
if not 0 <= SENS_PRUEBA <= 1:
    raise ValueError("La sensibilidad es una fracción entre 0 y 1, no un porcentaje: VP / (VP + FN).")
PREC_UMB = M_UMB["VP"] / max(1, M_UMB["VP"] + M_UMB["FP"])
COSTO_UMB = costo(M_UMB["VP"], M_UMB["FP"], M_UMB["FN"], C_FALLA_B)
COSTO_IA = costo(M_IA["VP"], M_IA["FP"], M_IA["FN"], C_FALLA_B)
S_ARB_TR, S_ARB_TE = arbol_sin_limite(TR, ULT, REAL_PRUEBA)
fila = TABLA[np.isclose(TABLA.umbral, UMBRAL_ALARMA)].iloc[0]
RESULTADOS = {"rul_A": rul_A, "precision_A": precision_A, "sens_A": sens_A, "costo_pred_A": costo_pred_A,
              "unidad_B": UNIDAD, "ciclo_hoy": CICLO_HOY, "u_B": U_B, "rul_pred_B": RUL_PRED_B,
              "rul_exp_B": -1.0 if np.isnan(RUL_EXP) else RUL_EXP, "rul_real_B": RUL_REAL, "c_falla_B": C_FALLA_B,
              "umbral_alarma": UMBRAL_ALARMA,
              "sens_entrena": float(fila.sensibilidad), "sens_prueba": SENS_PRUEBA, "prec_prueba": PREC_UMB,
              "sens_ia": SENS_IA, "prec_ia": PREC_IA, "costo_umbral": COSTO_UMB, "costo_ia": COSTO_IA}
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, M, nom in ((axs[0], M_UMB, f"Tu umbral {UMBRAL_ALARMA:.2f}"), (axs[1], M_IA, "Modelo de IA")):
    mat = np.array([[M["VP"], M["FP"]], [M["FN"], M["VN"]]])
    ax.imshow(mat, cmap="Blues")
    for (i, j), v in np.ndenumerate(mat):
        ax.text(j, i, str(v), ha="center", va="center", fontsize=14, color="white" if v > mat.max() / 2 else "black")
    ax.set_xticks([0, 1], ["fallaba pronto", "no"]); ax.set_yticks([0, 1], ["alarma", "sin alarma"]); ax.set_title(nom)
fig.suptitle(f"Matrices de confusión en 100 motores de prueba · {alumno.nombre}")
firma(fig, alumno, RESULTADOS); plt.tight_layout(rect=(0, 0.06, 1, 0.95)); plt.show()
print(f"Sensibilidad de tu umbral · en las decisiones de entrenamiento {fila.sensibilidad:.2f} · en prueba {SENS_PRUEBA:.2f}")
print(f"Costo en prueba · tu umbral {COSTO_UMB:,} · modelo de IA {COSTO_IA:,} miles de pesos")
print(f"Árbol de decisión sin límite (memoriza): sensibilidad {S_ARB_TR:.2f} en entrenamiento y {S_ARB_TE:.2f} en prueba")
"""),
          cu.md("""
### B5 · Conclusión
¿Qué tan cerca quedó la recta de la vida real de tu motor, y por qué? ¿Tu umbral funcionó igual en los motores
nuevos que en el entrenamiento? ¿El modelo de IA fue mejor, igual o peor que tu umbral en prueba, y qué haría falta
para usarlo en planta? Al menos 25 palabras, con tu vida remanente predicha, la real y las dos sensibilidades de
prueba.
"""),
          cu.code(h("CONCLUSION_B") + "\n\n"
                  "revisa_texto('Conclusión de la práctica', CONCLUSION_B,\n"
                  "             {'tu vida remanente predicha': RUL_PRED_B, 'la vida remanente real': RUL_REAL,\n"
                  "              'la sensibilidad de tu umbral en prueba': SENS_PRUEBA,\n"
                  "              'la sensibilidad del modelo de IA': SENS_IA}, minimo=25)"),
          cu.md("""
### Tabla y captura · CSV para tu hoja de resultados
La celda descarga `S8_<código>.csv` con la historia de tu motor: lo que se sabía hoy, lo que pasó después y la recta.
En tu hoja de resultados: abre la pestaña **CSV** → **Archivo → Importar → Subir** → elige el archivo → **Reemplazar
la hoja actual**. La pestaña Resultados se llena sola.
"""),
          cu.code("""
ciclos = np.arange(1, VIDA + 1)
hi = G.set_index("ciclo").HI.reindex(ciclos).to_numpy()
recta = HI_HOY_B + M_B * (ciclos - CICLO_HOY)
ruta = f"S8_{alumno.codigo}.csv"
exportar_csv(ruta, alumno, RESULTADOS,
             {"ciclo": ciclos,
              "HI_hasta_hoy": [round(float(v), 3) if c <= CICLO_HOY else "" for c, v in zip(ciclos, hi)],
              "HI_despues": [round(float(v), 3) if c > CICLO_HOY else "" for c, v in zip(ciclos, hi)],
              "recta": [round(float(v), 3) if c >= CICLO_HOY - 30 and v <= U_B + 0.1 else "" for c, v in zip(ciclos, recta)]},
             extra={"fuente": FUENTE, "motor": f"{UNIDAD}, hoy en el ciclo {CICLO_HOY}", "maquina": MAQUINA})
print("Archivo listo:", ruta, "· huella", huella(alumno, RESULTADOS))
try:
    from google.colab import files
    files.download(ruta)
except ImportError:
    pass
""")]
    C += [cu.md("""
## Del curso a tu proyecto integrador
Las ocho sesiones forman una cadena que puedes aplicar a una variable de tu trabajo:
**adquirir** con el intervalo y la resolución correctos (S1–S2) → **calibrar** y conocer la **incertidumbre** (S3–S4)
→ **filtrar** y ver la **tendencia** (S5) → **pronosticar** (S6) → saber **qué** falla con el espectro (S7) → decidir
**cuándo** intervenir con un **indicador de salud**, un **umbral** elegido por costo y su **matriz de confusión** (S8).
En tu proyecto: elige el indicador de salud de tu variable, su umbral y qué costaría cada tipo de error.
""")]
    C += cu.cierre()
    if prof:
        C += [cu.md("""
---
# Sólo profesor · Clave del grupo y verificación de los CSV
1. Pega en `CODIGOS` la lista de códigos del grupo y ejecuta: la tabla da los resultados esperados de la parte A y el
   motor de cada alumno.
2. Sube los CSV entregados y ejecuta la última celda: rehace la parte B de cada alumno con los mismos datos y con el
   umbral que eligió. Tolerancia: 2 %.
"""),
              cu.code('''
import glob
CODIGOS = """
217654321
219876543
""".split()
filas = []
for c in CODIGOS:
    a = identificar("Alumno Clave", c, SESION)
    d, k_ = datos_s8(a), clave_s8(a)
    cb = caso_b(a, TR)
    filas.append({"codigo": c, "maquina": d["MAQUINA"], **{x: round(float(v), 4) for x, v in k_.items()},
                  "motor": cb["UNIDAD"], "hoy": cb["CICLO_HOY"], "rul_pred_B": round((U_B - cb["HI_HOY_B"]) / cb["M_B"], 1),
                  "rul_real_B": cb["RUL_REAL"]})
CLAVE = pd.DataFrame(filas).set_index("codigo")
CLAVE
'''),
              cu.code('''
def _difiere(x, ref):
    return abs(x - ref) > 0.02 * max(abs(ref), 1e-3)

for ruta in sorted(glob.glob("S8_*.csv")):
    meta, res, _ = leer_csv_firmado(ruta)
    a = identificar("Alumno Clave", meta["codigo"], SESION)
    k_ = clave_s8(a)
    malos = [x for x in k_ if x not in res or _difiere(res[x], k_[x])]
    if FUENTE.startswith("SINTÉTICOS") or str(meta.get("fuente", "")).startswith("SINTÉTICOS"):
        malos.append("fuente sintética: revisar la parte B a mano")
    else:
        cb = caso_b(a, TR)
        cf = asignar(a, COSTOS_FALLA_B, salto=3)
        tab = tabla_umbrales(MOM, cf)
        u = res.get("umbral_alarma", float("nan"))
        mu = matriz(ULT.HI > u, REAL_PRUEBA)
        mi = matriz(IA.predict_proba(ULT[SENSORES])[:, 1] > corte_ia(IA, MOM, cf), REAL_PRUEBA)
        esperado = {"unidad_B": cb["UNIDAD"], "ciclo_hoy": cb["CICLO_HOY"], "u_B": U_B, "c_falla_B": cf,
                    "rul_pred_B": (U_B - cb["HI_HOY_B"]) / cb["M_B"], "rul_real_B": cb["RUL_REAL"],
                    "sens_prueba": mu["VP"] / (mu["VP"] + mu["FN"]), "sens_ia": mi["VP"] / (mi["VP"] + mi["FN"])}
        malos += [x for x, v in esperado.items() if x not in res or _difiere(res[x], v)]
        if not np.isclose(u, tab.loc[tab.costo.idxmin(), "umbral"]):
            malos.append(f"umbral {u} no es el de menor costo ({tab.loc[tab.costo.idxmin(), 'umbral']:.2f})")
    print(f"{ruta}: {meta['nombre']} · huella {'válida' if verificar_csv(ruta) else 'NO VÁLIDA'} · "
          f"umbral {res.get('umbral_alarma')} · " + ("resultados correctos" if not malos else "revisar: " + ", ".join(malos)))
''')]
    return C


def generar_hoja(salida=HOJA, csv_ejemplo=None):
    return hoja.generar(
        salida,
        resultados=[("rul_A", "★ Vida remanente de tu bomba (días)", "0.0"),
                    ("precision_A", "Precisión de la alarma de la flota", "0.000"),
                    ("sens_A", "Sensibilidad de la alarma de la flota", "0.000"),
                    ("costo_pred_A", "Costo con predictivo (miles de pesos)", "#,##0"),
                    ("unidad_B", "Tu motor de C-MAPSS", "0"),
                    ("ciclo_hoy", "Tu «hoy» (ciclo)", "0"),
                    ("rul_pred_B", "Vida remanente con la recta (ciclos)", "0.0"),
                    ("rul_exp_B", "Vida remanente con la exponencial (ciclos; −1: no se ajustó)", "0.0"),
                    ("rul_real_B", "Vida remanente real (ciclos)", "0"),
                    ("c_falla_B", "Tu costo de falla en operación, parte B (miles de pesos)", "0"),
                    ("umbral_alarma", "Umbral de alarma elegido (psia)", "0.00"),
                    ("sens_entrena", "Sensibilidad de tu umbral en entrenamiento", "0.00"),
                    ("sens_prueba", "Sensibilidad de tu umbral en prueba", "0.00"),
                    ("prec_prueba", "Precisión de tu umbral en prueba", "0.00"),
                    ("sens_ia", "Sensibilidad del modelo de IA en prueba", "0.00"),
                    ("prec_ia", "Precisión del modelo de IA en prueba", "0.00"),
                    ("costo_umbral", "Costo de tu umbral en prueba (miles de pesos)", "#,##0"),
                    ("costo_ia", "Costo del modelo de IA en prueba (miles de pesos)", "#,##0")],
        comparacion=("rul_real_B", "rul_pred_B", "Error de la recta respecto a la vida real (%)"),
        preguntas=["1. ¿Por qué la recta se equivocó en la vida remanente de tu motor y en qué sentido? ¿Qué margen "
                   "dejarías al programar la intervención? Usa tus valores de vida remanente.",
                   "2. ¿Usarías tu umbral o el modelo de IA en planta? Compara sensibilidad, precisión y costo en "
                   "prueba. ¿Quién debe tomar la decisión final, cómo explicarías la alarma al técnico y qué cambia "
                   "si los datos son reales y no simulados?"],
        tabla={"encabezado_csv": "ciclo", "x": ("A", "Ciclo"),
               "series": [("B", "Hasta hoy"), ("C", "Después"), ("D", "Recta")]},
        grafica={"titulo": "Indicador de salud de tu motor", "x": "Ciclo", "y": "s11 suavizada (psia)",
                 "tipo": "dispersion"},
        renglones=370,
        metadatos=(("Fuente de los datos", "fuente"), ("Motor", "motor"), ("Bomba (parte A)", "maquina")),
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
                          os.path.join(sys.argv[2], "S8_resuelto.ipynb"))
        print("  prueba:", ruta)
