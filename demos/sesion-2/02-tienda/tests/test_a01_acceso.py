"""A01 · Control de acceso: cada quien ve solo sus pedidos."""
from conftest import ANA, BETO


def test_ana_ve_su_pedido(cliente):
    r = cliente.get("/pedidos/1", headers=ANA)
    assert r.status_code == 200 and r.json["usuario"] == "ana"


def test_sin_sesion_401(cliente):
    assert cliente.get("/pedidos/1").status_code == 401


def test_ana_no_ve_el_pedido_de_beto(cliente):
    r = cliente.get("/pedidos/2", headers=ANA)
    assert r.status_code == 404, "Un pedido ajeno debe responder 404 (no revelar que existe)"
    assert "Dosquebradas" not in r.get_data(as_text=True)


def test_beto_tampoco_ve_el_de_ana(cliente):
    assert cliente.get("/pedidos/1", headers=BETO).status_code == 404
