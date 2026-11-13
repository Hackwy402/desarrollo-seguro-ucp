"""A05 · Inyección de comandos en la generación de reportes."""
import os

from conftest import ANA


def test_reporte_normal(cliente, tienda):
    r = cliente.post("/reportes", json={"nombre": "ventas-noviembre"}, headers=ANA)
    assert r.status_code == 200
    assert os.path.exists(os.path.join(tienda.REPORTES, "ventas-noviembre.tgz"))


def test_punto_y_coma_no_ejecuta(cliente, tienda, tmp_path):
    marca = tmp_path / "comprometido"
    r = cliente.post("/reportes", json={"nombre": f"x; touch {marca} #"}, headers=ANA)
    assert not marca.exists(), "Se ejecutó un comando inyectado"
    assert r.status_code == 400


def test_sustitucion_de_comando(cliente, tmp_path):
    marca = tmp_path / "sustitucion"
    cliente.post("/reportes", json={"nombre": f"$(touch {marca})"}, headers=ANA)
    assert not marca.exists()


def test_no_escribe_fuera_de_reportes(cliente, tmp_path):
    r = cliente.post("/reportes", json={"nombre": "../../fuera"}, headers=ANA)
    assert r.status_code == 400
