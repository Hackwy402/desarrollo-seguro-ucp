"""API3 · Autorización a nivel de propiedad: qué campos se leen y cuáles se escriben."""
from conftest import entrar, fila


def test_perfil_no_expone_secretos(cliente):
    r = cliente.get("/api/perfil", headers=entrar(cliente, "ana"))
    assert r.status_code == 200 and r.json["nombre"] == "Ana Gómez"
    assert "hash_clave" not in r.json, "El hash nunca sale de la API"
    assert r.json.get("documento") == "******3456", "El documento sale enmascarado: solo los 4 últimos dígitos"


def test_editar_nombre_funciona(cliente):
    r = cliente.patch("/api/perfil", json={"nombre": "Ana M. Gómez"}, headers=entrar(cliente, "ana"))
    assert r.status_code == 200 and r.json["nombre"] == "Ana M. Gómez"


def test_no_puede_volverse_admin(cliente, billetera):
    cliente.patch("/api/perfil", json={"rol": "admin"}, headers=entrar(cliente, "ana"))
    assert fila(billetera, "ana")["rol"] == "cliente"


def test_no_puede_cambiar_su_saldo(cliente, billetera):
    cliente.patch("/api/perfil", json={"nombre": "Ana", "saldo": 999999999}, headers=entrar(cliente, "ana"))
    assert fila(billetera, "ana")["saldo"] == 1250000


def test_campo_no_permitido_400(cliente):
    r = cliente.patch("/api/perfil", json={"hash_clave": "x"}, headers=entrar(cliente, "ana"))
    assert r.status_code == 400, "Un campo fuera de la lista blanca responde 400"
