"""API4 · Consumo de recursos: el cliente no decide cuánto trabajo hace el servidor."""
from conftest import entrar


def test_limite_razonable_funciona(cliente):
    r = cliente.get("/api/cuentas/1/movimientos?limite=50", headers=entrar(cliente, "ana"))
    assert r.status_code == 200 and len(r.json) == 50


def test_limite_enorme_se_acota(cliente):
    r = cliente.get("/api/cuentas/1/movimientos?limite=100000", headers=entrar(cliente, "ana"))
    assert r.status_code == 400 or len(r.json) <= 100, "Máximo 100 por página"


def test_limite_negativo(cliente):
    r = cliente.get("/api/cuentas/1/movimientos?limite=-1", headers=entrar(cliente, "ana"))
    assert r.status_code == 400 or len(r.json) <= 100, "En SQLite, LIMIT -1 significa «sin límite»"


def test_limite_no_numerico_400(cliente):
    r = cliente.get("/api/cuentas/1/movimientos?limite=todo", headers=entrar(cliente, "ana"))
    assert r.status_code == 400, "Entrada inválida: 400, no 500"
