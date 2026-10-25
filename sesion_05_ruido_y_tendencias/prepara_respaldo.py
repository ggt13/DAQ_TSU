"""Para el profesor: copia de respaldo de los datos de Open-Meteo que usa la práctica de la sesión 5.

El cuaderno descarga de Open-Meteo los 60 días de cada alumno (ventanas que empiezan entre el 13 de enero y el 13 de
marzo de 2025). Si ese día la página no responde, lee esta copia del repositorio. Se ejecuta una vez, en Colab o en la
computadora, y se sube el archivo que resulta:

    python prepara_respaldo.py
-> datos/open_meteo_gdl_2025.csv   columnas  time, temperature_2m  (hora local de Guadalajara, del 1 de enero al
                                    31 de mayo de 2025)

Fuente: Open-Meteo.com, Historical Weather API (modelo ERA5 de Copernicus/ECMWF, celda de unos 25 km), licencia CC BY 4.0.
"""
import json
import os
import urllib.request

import pandas as pd

URL = ("https://archive-api.open-meteo.com/v1/archive?latitude=20.67&longitude=-103.35&models=era5"
       "&start_date=2025-01-01&end_date=2025-05-31&hourly=temperature_2m&timezone=America%2FMexico_City")
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "open_meteo_gdl_2025.csv")

if __name__ == "__main__":
    with urllib.request.urlopen(URL, timeout=60) as resp:
        datos = json.load(resp)["hourly"]
    tabla = pd.DataFrame({"time": datos["time"], "temperature_2m": datos["temperature_2m"]})
    if tabla["temperature_2m"].isna().any():
        raise SystemExit("La descarga trae horas vacías; vuelva a intentarlo más tarde.")
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    with open(os.path.join(os.path.dirname(SALIDA), "README.md"), "w", encoding="utf-8") as f:
        f.write("# Datos de la sesión 5\n\n"
                "`open_meteo_gdl_2025.csv`: temperatura horaria a 2 m en Guadalajara (20.67 N, 103.35 O), hora local, "
                "del 1 de enero al 31 de mayo de 2025.\n\n"
                f"Origen: Open-Meteo.com, Historical Weather API (reanálisis ERA5). Descargado el "
                f"{pd.Timestamp.now():%Y-%m-%d}. Licencia CC BY 4.0: citar «Open-Meteo.com» y ERA5.\n")
    print(f"{SALIDA}: {len(tabla)} horas, de {tabla['time'].iloc[0]} a {tabla['time'].iloc[-1]}")
