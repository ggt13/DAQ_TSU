"""Pruebas de identidad.py. Ejecutar con:  python test_identidad.py"""
import os
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from identidad import (aparece, asignar, exportar_csv, firma, huella, identificar, leer_csv_firmado,
                       parametro, revisa, revisa_texto, verificar_csv)


def debe_fallar(nombre, codigo):
    try:
        identificar(nombre, codigo, "S2")
    except ValueError:
        return
    raise AssertionError(f"identificar({nombre!r}, {codigo!r}) debió detenerse")


# 1. La celda de identificación detiene el cuaderno con datos vacíos o de ejemplo
for n, c in [("", "217654321"), ("TU NOMBRE", "217654321"), ("Ana", "217654321"),
             ("Ana López", ""), ("Ana López", "000000000"), ("Ana López", "21A6543"), ("Ana López", "12")]:
    debe_fallar(n, c)

a = identificar("  Ana   López Ruiz ", "217654321", "S2")
b = identificar("Beto Díaz", "217654322", "S2")
assert a.nombre == "Ana López Ruiz"

# 2. Datos personales: iguales para el mismo código, distintos entre alumnos
assert parametro(a, "fs", 50, 200) == parametro(a, "fs", 50, 200)
assert parametro(a, "fs", 50, 200) != parametro(b, "fs", 50, 200)
assert 50 <= parametro(a, "fs", 50, 200) <= 200
# agregar una etiqueta nueva no cambia las anteriores
antes = parametro(a, "ruido", 0, 1)
parametro(a, "otra", 0, 1)
assert parametro(a, "ruido", 0, 1) == antes
# en un grupo de 30 casi no hay repetidos
grupo = [identificar("Alumno Prueba", str(217000000 + 37 * i), "S2") for i in range(30)]
assert len({parametro(x, "fs", 50, 200, 1) for x in grupo}) >= 28

# 3. Asignación por código: alumnos contiguos no comparten opción
assert asignar(a, ["Atemajac", "Centro", "Las Pintas"]) != asignar(b, ["Atemajac", "Centro", "Las Pintas"])

# 4. Huella: depende del código, la sesión y los resultados
r = {"lsb_mV": 4.8828125, "error_max": 2.44}
assert huella(a, r) == huella(a, dict(reversed(list(r.items()))))
assert huella(a, r) != huella(b, r)
assert huella(a, r) != huella(a, {"lsb_mV": 4.9, "error_max": 2.44})
assert len(huella(a, r)) == 6

# 5. CSV firmado: se lee y su huella se verifica; si alguien cambia un resultado, falla
with tempfile.TemporaryDirectory() as d:
    ruta = os.path.join(d, "S2_217654321_Lopez.csv")
    exportar_csv(ruta, a, r, {"t_s": [0, 0.01, 0.02], "v_V": [0.0, 1.2, 2.4]}, extra={"fuente": "prueba"})
    meta, res, tabla = leer_csv_firmado(ruta)
    assert meta["nombre"] == "Ana López Ruiz" and meta["codigo"] == "217654321" and meta["fuente"] == "prueba"
    assert tabla[0] == ["t_s", "v_V"] and len(tabla) == 4
    assert verificar_csv(ruta)
    texto = open(ruta, encoding="utf-8").read().replace("resultado:error_max,2.44", "resultado:error_max,2.5")
    open(ruta, "w", encoding="utf-8").write(texto)
    assert not verificar_csv(ruta)

# 6. Firma en la figura
fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1])
firma(fig, a, r)
assert getattr(fig, "_firmada", False)
assert any("217654321" in t.get_text() and huella(a, r) in t.get_text() for t in fig.texts)


# 7. Revisión de ejercicios: completo pasa; incompleto se detiene y dice qué falta
def falla(*args, **kw):
    try:
        (kw.pop("f", revisa))(*args, **kw)
    except ValueError as e:
        return str(e)
    raise AssertionError("debió detenerse")

lsb = 70 / 2 ** 10
pred = "las lecturas sólo cambian en saltos de un LSB, unas siete centésimas de grado"
revisa(1, lsb, "70 / 2**10 = 0.0684 °C", pred, [70, 10], ["°C"])
assert "expresión" in falla(1, None, "70 / 2**10 = 0.0684 °C", pred, [70, 10], ["°C"])
assert "tu dato 10" in falla(1, lsb, "70 / 2**8 = 0.0684 °C", pred, [70, 10], ["°C"])
assert "resultado" in falla(1, lsb, "70 / 2**10 = 0.27 °C", pred, [70, 10], ["°C"])
assert "unidad" in falla(1, lsb, "70 / 2**10 = 0.0684", pred, [70, 10], ["°C"])
assert "10 palabras" in falla(1, lsb, "70 / 2**10 = 0.0684 °C", "saltos", [70, 10], ["°C"])
assert aparece(32000, "32 000 × 60 s") and aparece(32000, "32,000") and aparece(0.0684, "0,0684")
revisa(3, 32000 * 60 / 86400, "32 000 × 60 / 86 400 = 22.2 días", pred, [32000, 60], ["día"])
revisa_texto("Conclusión", "El error que obtuve fue 0.0337 °C y el predicho 0.0342 °C, así que el redondeo "
             "nunca pasó de medio escalón del convertidor de diez bits en toda la semana",
             {"el error obtenido": 0.0337, "el error predicho": 0.0342})
m = falla("Conclusión", "El error fue 0.0337 y quedó dentro de lo esperado según la teoría "
          "del redondeo a medio escalón en toda la semana registrada",
          {"el error obtenido": 0.0337, "el error predicho": 0.0342}, f=revisa_texto)
assert "el error predicho" in m and "0.0342" not in m

# 8. Números escritos como los escribe una persona
for x, t, esperado in [(34271.6, "= 34272 s", True), (123456.7, "= 123456.7 s", True), (0.0342, "0.03", False),
                       (120.0, "1200", False), (120.0, "= 120.0 h", True), (0.0342, "0.034200", True),
                       (0.390625, "0.39 %", True), (10, "100", False), (10, "2**10", True)]:
    assert aparece(x, t) == esperado, (x, t)

print("identidad.py: todas las pruebas pasan")
