"""Prueba de los cuadernos de una o varias sesiones, antes de subirlos.

Uso:  python comun/prueba_cuadernos.py 1 2 3 4      (números de sesión; sin argumentos, todas las que tengan gen_sN.py)

Para cada sesión:
  1. genera los archivos y dos versiones resueltas: con las expresiones del profesor y como un alumno que escribe
     los números con 4 cifras significativas;
  2. ejecuta las dos versiones con varios códigos de alumno;
  3. ejecuta la versión del alumno en blanco (debe detenerse en la identificación) y con la identificación llena
     (debe detenerse en el ejercicio 1);
  4. ejecuta la versión del profesor con los CSV producidos: todas las huellas deben ser válidas y los resultados
     correctos dentro de la tolerancia.
"""
import glob
import os
import random
import subprocess
import sys
import tempfile

import nbclient
import nbformat

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ejecuta(nb, carpeta):
    try:
        nbclient.NotebookClient(nb, timeout=240, kernel_name="python3",
                                resources={"metadata": {"path": carpeta}}).execute()
        return None
    except Exception as e:  # noqa: BLE001
        return str(e).strip().splitlines()[-1]


def con_codigo(ruta, codigo, nombre=None):
    nb = nbformat.read(ruta, 4)
    for c in nb.cells:
        if c.cell_type == "code" and c.source.startswith("NOMBRE"):
            if nombre:
                c.source = c.source.replace('NOMBRE = ""', f'NOMBRE = "{nombre}"').replace('CODIGO = ""', f'CODIGO = "{codigo}"')
            else:
                c.source = c.source.replace("217654321", codigo)
    return nb


def prueba(n, codigos):
    carpeta = glob.glob(os.path.join(RAIZ, f"sesion_0{n}_*"))[0]
    gen = os.path.join(carpeta, f"gen_s{n}.py")
    tmp = tempfile.mkdtemp(prefix=f"s{n}_")
    subprocess.run([sys.executable, gen, "--prueba", tmp], check=True, capture_output=True)
    fallas = 0
    for version in (f"S{n}_resuelto.ipynb", f"S{n}_numeros.ipynb"):
        for c in codigos:
            err = ejecuta(con_codigo(os.path.join(tmp, version), c), tmp)
            if err:
                fallas += 1
                print(f"  ✘ {version} {c}: {err[-160:]}")
    alumno = os.path.join(carpeta, f"S{n}_AC_CLASE_Colab_ALUMNO.ipynb")
    e1 = ejecuta(nbformat.read(alumno, 4), tmp) or ""
    e2 = ejecuta(con_codigo(alumno, "219876543", "Beto Díaz"), tmp) or ""
    ok_blanco = "NOMBRE" in e1 and "Ejercicio 1" in e2
    prof = con_codigo(os.path.join(carpeta, f"S{n}_AC_CLASE_Colab_PROF.ipynb"), "219876543", "Guillermo García")
    e3 = ejecuta(prof, tmp)
    salida = "".join(o.get("text", "") for o in prof.cells[-1].get("outputs", []))
    malos = [l for l in salida.splitlines() if "NO VÁLIDA" in l or "revisar" in l]
    print(f"S{n}: {2 * len(codigos) - fallas}/{2 * len(codigos)} ejecuciones completas · en blanco "
          f"{'se detiene bien' if ok_blanco else 'NO SE DETIENE BIEN'} · profesor: "
          + (f"falla ({e3[-120:]})" if e3 else f"{salida.count('.csv')} CSV, {len(malos)} con problemas"))
    for l in malos:
        print("   ", l)
    return fallas + (not ok_blanco) + bool(e3) + len(malos)


if __name__ == "__main__":
    sesiones = [int(a) for a in sys.argv[1:]] or sorted(
        int(os.path.basename(p)[5]) for p in glob.glob(os.path.join(RAIZ, "sesion_0*", "gen_s*.py")))
    random.seed(2027)
    codigos = ["217654321", "219876543"] + [str(random.randint(215000000, 224999999)) for _ in range(4)]
    total = sum(prueba(n, codigos) for n in sesiones)
    print("Todo en orden." if total == 0 else f"{total} problemas.")
    sys.exit(1 if total else 0)
