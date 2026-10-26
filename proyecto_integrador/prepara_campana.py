"""Para el profesor: convierte el archivo de una campaña RC-5 al CSV que lee el cuaderno del proyecto.

Uso (con el archivo exportado de ElitechLog):
    python prepara_campana.py 1 RC5_campana1.xlsx "Refrigerador de pasta de soldadura, repisa central"
-> datos/campana_1.csv   (fecha_hora, temperatura)
-> datos/campanas.csv    (una fila por campaña: n, lugar, inicio, fin, intervalo_s, lecturas)

Usa el mismo lector que el cuaderno (DATOS_PI de gen_pi.py), así que si aquí lee bien, en Colab también. Recorte antes
las horas en que el registrador no estaba en su lugar, con --inicio y --fin en horas:
    python prepara_campana.py 2 RC5_2.xlsx "Cuarto de servidores" --inicio 1.5 --fin 0.5
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import gen_pi  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("n", type=int, choices=[1, 2, 3])
    p.add_argument("archivo")
    p.add_argument("lugar")
    p.add_argument("--inicio", type=float, default=0.0)
    p.add_argument("--fin", type=float, default=0.0)
    a = p.parse_args()
    ns = {"np": np}
    exec(open(os.path.join(AQUI, "..", "comun", "identidad.py"), encoding="utf-8").read(), ns)
    exec(gen_pi.DATOS_PI, ns)
    tabla = ns["lee_registro"](a.archivo)
    s = ns["recorta"](tabla.iloc[:, 0].dropna(), a.inicio, a.fin)
    q = ns["calidad"](s)
    os.makedirs(os.path.join(AQUI, "datos"), exist_ok=True)
    salida = os.path.join(AQUI, "datos", f"campana_{a.n}.csv")
    pd.DataFrame({"fecha_hora": s.index.strftime("%Y-%m-%d %H:%M:%S"), "temperatura": s.values}).to_csv(salida, index=False)
    lista = os.path.join(AQUI, "datos", "campanas.csv")
    filas = pd.read_csv(lista) if os.path.exists(lista) else pd.DataFrame(
        columns=["n", "lugar", "inicio", "fin", "intervalo_s", "lecturas"])
    filas = filas[filas["n"] != a.n]
    filas.loc[len(filas)] = [a.n, a.lugar, f"{s.index[0]:%Y-%m-%d %H:%M}", f"{s.index[-1]:%Y-%m-%d %H:%M}",
                             q["DT_EF_S"], q["N_LECT"]]
    filas.sort_values("n").to_csv(lista, index=False)
    print(f"{salida}: {q['N_LECT']} lecturas cada {q['DT_EF_S']:g} s, {q['DIAS_REG']:.2f} días, "
          f"{q['N_HUECOS']} huecos ({q['HORAS_HUECOS']:.1f} h), escalón {q['ESCALON']:g}")
    print("Súbalo al repositorio (datos/campana_N.csv y datos/campanas.csv) y el cuaderno lo descargará solo.")


if __name__ == "__main__":
    main()
