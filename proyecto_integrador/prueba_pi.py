"""Prueba del cuaderno del proyecto integrador antes de subirlo.

Uso:  python proyecto_integrador/prueba_pi.py

1. Prueba las funciones del cuaderno con datos de resultado conocido: lectura de un CSV tipo Govee (°F), de un Excel
   tipo ElitechLog (día/mes) y de un CSV con punto y coma y coma decimal; huecos y escalón; ciclo dominante; alarmas
   con confirmación e histéresis.
2. Ejecuta las versiones resueltas (expresiones del profesor y números con 4 cifras) con cada fuente de registro y
   varios códigos.
3. Ejecuta la versión del alumno en blanco: debe detenerse en la identificación, luego en el plan y luego en las
   predicciones.
4. Ejecuta la versión del profesor con los CSV producidos: todas las huellas deben ser válidas.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import nbclient
import nbformat
import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import gen_pi  # noqa: E402

CODIGOS = ["217654321", "219876543", "221034567"]


def ejecuta(nb, carpeta):
    try:
        nbclient.NotebookClient(nb, timeout=300, kernel_name="python3",
                                resources={"metadata": {"path": carpeta}}).execute()
        return None
    except Exception as e:  # noqa: BLE001
        return str(e).strip().splitlines()[-1]


def con(nb, cambios):
    """Reemplaza renglones que empiezan con «VAR =» por los dados."""
    nb = nbformat.from_dict(nb)
    for c in nb.cells:
        if c.cell_type != "code":
            continue
        lineas = c.source.split("\n")
        for i, l in enumerate(lineas):
            for var, valor in cambios.items():
                if l.startswith(var + " ="):
                    lineas[i] = f"{var} = {valor}"
        c.source = "\n".join(lineas)
    return nb


def archivos_de_prueba(d):
    t = pd.date_range("2027-03-01 09:00", periods=7 * 1440, freq="60s")
    x = np.arange(t.size) / 1440
    T = 23 + 2 * np.sin(2 * np.pi * x) + np.random.default_rng(1).normal(0, 0.1, t.size)
    HR = 45 + 8 * np.sin(2 * np.pi * x + 1)
    keep = np.ones(t.size, bool); keep[3000:3180] = False                      # hueco de 3 h
    g = pd.DataFrame({"Timestamp for sample frequency every 1 min min": t[keep].strftime("%Y-%m-%d %H:%M:%S"),
                      "Temperature_Fahrenheit": np.round(T[keep] * 9 / 5 + 32, 1),
                      "Relative_Humidity": np.round(HR[keep], 1)})
    g.to_csv(os.path.join(d, "govee.csv"), index=False)
    # Excel tipo ElitechLog: renglones de informe, encabezado y fechas día/mes
    t2 = pd.date_range("2027-03-13 08:00", periods=3 * 2880, freq="30s")
    T2 = 5 + 1.5 * np.sign(np.sin(2 * np.pi * np.arange(t2.size) * 30 / 1200)) + 0.3
    filas = [["Elitech RC-5", None, None], ["Device ID", "EF123", None], [None, None, None],
             ["No.", "Time", "Temperature(°C)"]]
    filas += [[i + 1, ti.strftime("%d/%m/%Y %H:%M:%S"), round(v, 1)] for i, (ti, v) in enumerate(zip(t2, T2))]
    pd.DataFrame(filas).to_excel(os.path.join(d, "elitech.xlsx"), header=False, index=False)
    # CSV de un área: punto y coma, coma decimal
    t3 = pd.date_range("2027-03-02 00:00", periods=4 * 288, freq="300s")
    v3 = 1.8 + 0.05 * np.arange(t3.size) / 288 + 0.2 * np.sin(2 * np.pi * np.arange(t3.size) / 288)
    with open(os.path.join(d, "area.csv"), "w", encoding="utf-8") as f:
        f.write("fecha_hora;presion_bar\n")
        for ti, v in zip(t3, v3):
            f.write(f"{ti:%Y-%m-%d %H:%M};" + f"{v:.3f}".replace(".", ",") + "\n")
    return T, HR


def prueba_funciones(d):
    ns = {}
    exec(open(os.path.join(RAIZ, "comun", "identidad.py"), encoding="utf-8").read(), ns)
    exec(gen_pi.DATOS_PI, ns)
    malos = []
    g = ns["lee_registro"](os.path.join(d, "govee.csv"))
    if g.index[0] != pd.Timestamp("2027-03-01 09:00"):
        malos.append(f"Govee: la fecha inicial se leyó como {g.index[0]}")
    if set(g.columns) != {"temperatura", "humedad"}:
        malos.append(f"Govee: columnas {list(g.columns)}")
    if abs(g["temperatura"].mean() - 23) > 0.2:
        malos.append(f"Govee: °F no convertidos ({g['temperatura'].mean():.2f})")
    q = ns["calidad"](g["temperatura"])
    if q["N_HUECOS"] != 1 or abs(q["HORAS_HUECOS"] - 3) > 0.05 or q["DT_EF_S"] != 60:
        malos.append(f"Govee: huecos {q['N_HUECOS']}, {q['HORAS_HUECOS']:.2f} h, dt {q['DT_EF_S']}")
    u = ns["rejilla"](g["temperatura"], 60)
    c = ns["ciclo_dominante"](u, 60)
    if abs(c - 24) > 1.5:
        malos.append(f"ciclo dominante {c:.2f} h, no 24")
    e = ns["lee_registro"](os.path.join(d, "elitech.xlsx"))
    if len(e) != 3 * 2880 or e.index[0] != pd.Timestamp("2027-03-13 08:00") or list(e.columns) != ["temperatura"]:
        malos.append(f"ElitechLog: {len(e)} renglones, inicio {e.index[0]}, columnas {list(e.columns)}")
    ue = ns["rejilla"](e.iloc[:, 0], 30)
    ce = ns["ciclo_dominante"](ue, 30)
    if abs(ce - 1200 / 3600) > 0.03:
        malos.append(f"ciclo del compresor {ce * 60:.1f} min, no 20")
    a = ns["lee_registro"](os.path.join(d, "area.csv"))
    if len(a) != 4 * 288 or list(a.columns) != ["presion_bar"] or abs(a.iloc[0, 0] - 1.8) > 0.01:
        malos.append(f"área: {len(a)} renglones, columnas {list(a.columns)}, primer valor {a.iloc[0, 0]}")
    # alarmas: un pico de una lectura (no se confirma con 3 min), una excursión de 30 min y luego el valor ronda el
    # límite sin bajar de límite − histéresis (la alarma sigue encendida) hasta que baja a 7.4 y se apaga
    t = pd.date_range("2027-01-01", periods=600, freq="60s")
    y = np.full(600, 5.0)
    y[100] = 9
    y[300:330] = 8.5
    y[330:340] = [7.9, 8.1] * 5
    y[340:350] = 7.4
    cr, ev, hf = ns["alarmas"](pd.Series(y, index=t), 8.0, "arriba", 3, 0.5, 60)
    if cr != 7 or ev != [(303, 340)]:
        malos.append(f"alarmas: cruces {cr}, eventos {ev}")
    cr2, ev2, _ = ns["alarmas"](pd.Series(-y, index=t), -8.0, "abajo", 3, 0.5, 60)
    if (cr2, len(ev2)) != (cr, len(ev)):
        malos.append("alarmas «abajo» no simétricas")
    q2 = ns["calidad"](pd.Series(np.round(np.linspace(20, 21, 50), 1), index=t[:50]))
    if q2["ESCALON"] != 0.1:
        malos.append(f"escalón {q2['ESCALON']}")
    malos += prueba_casos_dificiles(ns, d)
    print("Funciones:", "todo en orden" if not malos else "; ".join(malos))
    return len(malos)


def prueba_casos_dificiles(ns, d):
    """Casos de la revisión independiente: fechas ambiguas, fecha y hora separadas, unidades pegadas, miles, zona
    horaria, informe con fechas antes de la tabla, ciclo con deriva, registros cortos y horas fuera con huecos."""
    malos = []
    rng = np.random.default_rng(7)
    # fechas día/mes ambiguas: del 1 al 3 de febrero, Excel con informe que trae fechas y un renglón Max
    t = pd.date_range("2027-02-01 00:00", periods=3 * 1440, freq="60s")
    filas = [["Elitech RC-5", None, None], ["Start Time", "01/02/2027 00:00:00", None],
             ["Max", "01/02/2027 00:00:00", "7.5"], [None, None, None], ["No.", "Time", "Temperature(°C)"]]
    filas += [[i + 1, ti.strftime("%d/%m/%Y %H:%M:%S"), "5.0"] for i, ti in enumerate(t)]
    pd.DataFrame(filas).to_excel(os.path.join(d, "ambiguo.xlsx"), header=False, index=False)
    e = ns["lee_registro"](os.path.join(d, "ambiguo.xlsx"))
    if e.index[0] != t[0] or e.index[-1] != t[-1] or len(e) != t.size or list(e.columns) != ["temperatura"] \
            or e.iloc[0, 0] != 5.0:
        malos.append(f"fechas ambiguas: {e.index[0]}–{e.index[-1]}, {len(e)} renglones, {list(e.columns)}, "
                     f"primer valor {e.iloc[0, 0]}")
    # fecha y hora en columnas separadas, con unidades pegadas
    with open(os.path.join(d, "separadas.csv"), "w", encoding="utf-8") as f:
        f.write("Fecha,Hora,Temperatura\n")
        for ti in t[:500]:
            f.write(f"{ti:%d/%m/%Y},{ti:%H:%M},23.4°C\n")
    sp = ns["lee_registro"](os.path.join(d, "separadas.csv"))
    if len(sp) != 500 or sp.iloc[0, 0] != 23.4 or sp.index[1] - sp.index[0] != pd.Timedelta("60s"):
        malos.append(f"fecha y hora separadas: {len(sp)} renglones, {sp.iloc[0, 0] if len(sp) else '—'}")
    # separador de miles y zona horaria ISO
    with open(os.path.join(d, "miles.csv"), "w", encoding="utf-8") as f:
        f.write("timestamp,presion_pa\n")
        for ti in t[:300]:
            f.write(f'{ti:%Y-%m-%dT%H:%M:%S}-06:00,"101,325.2"\n')
    m = ns["lee_registro"](os.path.join(d, "miles.csv"))
    if abs(m.iloc[0, 0] - 101325.2) > 0.01 or m.index[0] != t[0]:
        malos.append(f"miles o zona horaria: {m.iloc[0, 0]} en {m.index[0]}")
    # ciclo diario pequeño con deriva lenta (caminata aleatoria): debe seguir dando 24 h
    tt = pd.date_range("2027-02-01", periods=7 * 288, freq="300s")
    x = np.arange(tt.size) / 288
    bien = 0
    for k in range(20):
        r = np.random.default_rng(k)
        v = 22 + 0.5 * np.sin(2 * np.pi * x) + np.cumsum(r.normal(0, 0.02, tt.size)) + r.normal(0, 0.1, tt.size)
        c = ns["ciclo_dominante"](pd.Series(v, index=tt), 300)
        bien += np.isfinite(c) and abs(c - 24) < 1.5
    if bien < 16:
        malos.append(f"ciclo con deriva: 24 h en {bien} de 20")
    un_dia = pd.Series(22 + np.sin(2 * np.pi * x[:288]), index=tt[:288])
    if np.isfinite(ns["ciclo_dominante"](un_dia, 300)) or np.isfinite(ns["tendencia"](un_dia)[0]):
        malos.append("registro de 1 día: no debe dar ciclo ni tendencia")
    if np.isfinite(ns["ciclo_dominante"](pd.Series(np.full(tt.size, 5.0), index=tt), 300)):
        malos.append("señal plana: no debe dar ciclo")
    m_t = ns["tendencia"](pd.Series(20 + 0.2 * x + np.sin(2 * np.pi * x), index=tt))[0]
    if abs(m_t - 0.2) > 0.02:
        malos.append(f"tendencia de 0.2 por día: {m_t:.3f}")
    # horas fuera del límite con un hueco largo: el hueco no cuenta
    y = pd.Series(np.full(100, 5.0), index=pd.date_range("2027-01-01", periods=100, freq="60s"))
    y.iloc[10:20] = 9.0
    y.iloc[20:80] = np.nan
    _, _, hf = ns["alarmas"](y, 8.0, "arriba", 0, 0.5, 60)
    if abs(hf - 10 / 60) > 1e-6:
        malos.append(f"horas fuera con hueco: {hf:.3f} h, no 0.167")
    # unidades del plan contra la columna
    for col, uni, debe in [("temperatura", "°F", True), ("temperatura", "°C", False), ("humedad", "°C", True),
                           ("humedad", "%HR", False)]:
        try:
            ns["revisa_unidad"](uni, col)
            fallo = False
        except ValueError:
            fallo = True
        if fallo != debe:
            malos.append(f"revisa_unidad({uni}, {col})")
    return malos


CASOS = [("campaña 1", '""', '"temperatura"', {}),
         ("govee", '"govee.csv"', '"temperatura"', {"LIMITE": "24.5", "PRED_MIN": "19", "PRED_MAX": "26"}),
         ("govee", '"govee.csv"', '"humedad"', {"UNIDAD": '"%HR"', "LIMITE": "55", "EXACT_INSTR": "3.0",
                                                 "EXACT_REQ": "5.0", "PRED_MIN": "30", "PRED_MAX": "60"}),
         ("area", '"elitech.xlsx"', '""', {}),
         ("area", '"area.csv"', '""', {"UNIDAD": '"bar"', "LIMITE": "2.0", "HISTERESIS": "0.05",
                                       "EXACT_REQ": "0.05", "EXACT_INSTR": "0.01", "PRED_MIN": "1.5",
                                       "PRED_MAX": "2.2", "PRED_TEND": "0.05"})]


def con_url(nb, url):
    nb = nbformat.from_dict(nb)
    for c in nb.cells:
        if c.cell_type == "code" and "URL_DATOS = " in c.source:
            c.source = "\n".join((f'URL_DATOS = "{url}"' if l.startswith("URL_DATOS = ") else l)
                                  for l in c.source.split("\n"))
    return nb


def prueba_campana_real(tmp):
    """La campaña 2 armada con prepara_campana.py y servida como file://: no debe caer al registro sintético."""
    datos = os.path.join(tmp, "repo_datos")
    os.makedirs(datos, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(AQUI, "prepara_campana.py"), "2", os.path.join(tmp, "elitech.xlsx"),
                        "Cuarto de prueba"], capture_output=True, text=True)
    for f in ("campana_2.csv", "campanas.csv"):
        shutil.move(os.path.join(AQUI, "datos", f), os.path.join(datos, f))
    nb = con_url(con(nbformat.read(os.path.join(tmp, "PI_resuelto.ipynb"), 4),
                     {"FUENTE_REG": '"campaña 2"', "CODIGO": '"219876543"'}), "file://" + datos + "/")
    err = ejecuta(nb, tmp)
    salida = "".join(o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", [])
                     if o.get("name") == "stdout")
    ok = not err and "Campaña RC-5 n.º 2 del grupo · Cuarto de prueba" in salida and "SINTÉTICO" not in salida
    print(f"Campaña real (prepara_campana.py → file://): {'bien' if ok else 'FALLA: ' + str(err or r.stderr)[-200:]}")
    for f in glob.glob(os.path.join(tmp, "PI_2*.csv")):
        os.remove(f)
    return 0 if ok else 1


def revisa_numeros_govee(tmp):
    """Los números del CSV del caso Govee (temperatura) contra lo que se armó: 60 s, un hueco de 3 h, ciclo de 24 h."""
    sys.path.insert(0, os.path.join(RAIZ, "comun"))
    import identidad
    ruta = sorted(glob.glob(os.path.join(tmp, "PI_1r_*.csv")))[0]
    _, res, _ = identidad.leer_csv_firmado(ruta)
    esperado = {"dt_ef_s": 60, "n_huecos": 1, "horas_huecos": 3.0, "ciclo_h": 24.0, "sintetico": 0, "fuente_n": 1}
    malos = [f"{k}={res.get(k)}" for k, v in esperado.items()
             if k not in res or abs(res[k] - v) > (0.05 if k != "ciclo_h" else 1.0)]
    print("Números del caso Govee:", "bien" if not malos else "NO: " + ", ".join(malos))
    return len(malos)


def prueba_huella(tmp):
    """Editar un resultado invalida la huella; cambiar a mano la fuente no borra la marca de sintético."""
    sys.path.insert(0, os.path.join(RAIZ, "comun"))
    import identidad
    ruta = sorted(glob.glob(os.path.join(tmp, "PI_0r_*.csv")))[0]          # campaña 1, sintética
    texto = open(ruta, encoding="utf-8").read()
    malos = []
    alterado = os.path.join(tmp, "alterado.csv")
    linea = next(l for l in texto.splitlines() if l.startswith("resultado:max_obt,"))
    open(alterado, "w", encoding="utf-8").write(texto.replace(linea, "resultado:max_obt,7.9"))
    if identidad.verificar_csv(alterado):
        malos.append("un máximo editado conserva la huella")
    fuente = next(l for l in texto.splitlines() if l.startswith("fuente,"))
    open(alterado, "w", encoding="utf-8").write(texto.replace(fuente, "fuente,Campaña RC-5 n.º 1 del grupo"))
    _, res, _ = identidad.leer_csv_firmado(alterado)
    if not identidad.verificar_csv(alterado) or res.get("sintetico") != 1:
        malos.append("cambiar la fuente a mano borra la marca de sintético")
    os.remove(alterado)
    print("Huella:", "bien" if not malos else "; ".join(malos))
    return len(malos)


def main():
    tmp = tempfile.mkdtemp(prefix="pi_")
    subprocess.run([sys.executable, os.path.join(AQUI, "gen_pi.py"), "--prueba", tmp], check=True, capture_output=True)
    archivos_de_prueba(tmp)
    total = prueba_funciones(tmp)
    hechas = 0
    for version in ("PI_resuelto.ipynb", "PI_numeros.ipynb"):
        base = nbformat.read(os.path.join(tmp, version), 4)
        for k, (fuente, archivo, columna, extra) in enumerate(CASOS):
            codigo = CODIGOS[k % len(CODIGOS)]
            nb = con(base, {"FUENTE_REG": f'"{fuente}"', "ARCHIVO": archivo, "COLUMNA": columna,
                            "CODIGO": f'"{codigo}"', **extra})
            err = ejecuta(nb, tmp)
            hechas += 1
            if err:
                total += 1
                print(f"  ✘ {version} · {fuente} {archivo} {columna}: {err[-200:]}")
            else:
                salida = "".join(o.get("text", "") for c in nb.cells if c.cell_type == "code"
                                 for o in c.get("outputs", []) if o.get("name") == "stdout")
                linea = [l for l in salida.splitlines() if l.startswith("Cruces simples")]
                print(f"  ✔ {version} · {fuente} {archivo} {columna} · {linea[0] if linea else ''}")
            for f in glob.glob(os.path.join(tmp, "PI_2*.csv")):
                shutil.move(f, f.replace("PI_2", f"PI_{k}{version[3]}_2"))  # guarda el CSV de cada caso
    total += prueba_campana_real(tmp)
    total += revisa_numeros_govee(tmp)
    total += prueba_huella(tmp)
    # Versión del alumno en blanco
    alumno = nbformat.read(gen_pi.ALUMNO, 4)
    e1 = ejecuta(nbformat.from_dict(alumno), tmp) or ""
    e2 = ejecuta(con(alumno, {"NOMBRE": '"Beto Díaz"', "CODIGO": '"219876543"'}), tmp) or ""
    plan = {v: gen_pi.SOL[v] for v in ("VARIABLE", "UNIDAD", "P_PLAN_S", "DT_PLAN_S", "EXACT_REQ", "EXACT_INSTR",
                                       "LIMITE", "SENTIDO", "CONFIRMA_MIN", "HISTERESIS", "VENTANA_MIN")}
    e3 = ejecuta(con(alumno, {"NOMBRE": '"Beto Díaz"', "CODIGO": '"219876543"', **plan}), tmp) or ""
    malo_plan = dict(plan, DT_PLAN_S="900")
    e4 = ejecuta(con(alumno, {"NOMBRE": '"Beto Díaz"', "CODIGO": '"219876543"', **malo_plan}), tmp) or ""
    bien = ["NOMBRE" in e1, "Plan: falta" in e2, "Predicciones: falta" in e3, "P/2" in e4]
    print(f"Alumno en blanco: identificación {bien[0]} · plan vacío {bien[1]} · predicciones vacías {bien[2]} · "
          f"intervalo que no cumple Nyquist {bien[3]}")
    total += bien.count(False)
    if not all(bien):
        print("   ", e1[-120:], "|", e2[-120:], "|", e3[-120:], "|", e4[-120:])
    # Profesor: renombra los CSV de los casos como PI_<n>.csv para que los encuentre
    for i, f in enumerate(sorted(glob.glob(os.path.join(tmp, "PI_*_2*.csv")))):
        shutil.move(f, os.path.join(tmp, f"PI_caso{i:02d}.csv"))
    prof = con(nbformat.read(gen_pi.PROF, 4), {"NOMBRE": '"Guillermo García"', "CODIGO": '"219876543"'})
    e5 = ejecuta(prof, tmp)
    salida = "".join(o.get("text", "") for o in prof.cells[-1].get("outputs", []) if o.get("name") == "stdout")
    n_csv = salida.count(".csv")
    malos = [l for l in salida.splitlines() if "NO VÁLIDA" in l]
    print(f"Profesor: {'falla: ' + e5[-150:] if e5 else f'{n_csv} CSV, {len(malos)} con huella no válida'}")
    total += bool(e5) + len(malos) + (n_csv < hechas)
    print(f"{hechas} ejecuciones resueltas.", "Todo en orden." if total == 0 else f"{total} problemas.")
    return total


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
