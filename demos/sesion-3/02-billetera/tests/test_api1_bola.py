"""API1 · Autorización a nivel de objeto: cada quien ve solo sus cuentas."""
from conftest import entrar


def test_ana_ve_sus_movimientos(cliente):
    r = cliente.get("/api/cuentas/1/movimientos", headers=entrar(cliente, "ana"))
    assert r.status_code == 200 and len(r.json) == 20


def test_sin_sesion_401(cliente):
    assert cliente.get("/api/cuentas/1/movimientos").status_code == 401


def test_ana_no_ve_la_cuenta_de_beto(cliente):
    r = cliente.get("/api/cuentas/2/movimientos", headers=entrar(cliente, "ana"))
    assert r.status_code == 404, "Una cuenta ajena responde 404"
    assert "Nómina" not in r.get_data(as_text=True)


def test_cuenta_inexistente_404(cliente):
    assert cliente.get("/api/cuentas/77/movimientos", headers=entrar(cliente, "beto")).status_code == 404
