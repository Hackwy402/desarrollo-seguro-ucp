"""V6 · Contraseñas: Argon2id con sal y una política mínima."""
from conftest import CLAVES, entrar, fila


def test_login_sigue_funcionando(cliente):
    entrar(cliente, "ana")


def test_hash_es_argon2id(cliente, billetera):
    cliente.get("/salud")
    entrar(cliente, "ana")
    assert fila(billetera, "ana")["hash_clave"].startswith("$argon2id$"), "Use Argon2id (argon2-cffi)"


def test_misma_clave_distinto_hash(cliente, billetera):
    for u in ("carla", "dario"):
        r = cliente.post("/api/registro", json={"usuario": u, "clave": "Misma-clave-para-los-dos-1", "documento": "1"})
        assert r.status_code == 201
    assert fila(billetera, "carla")["hash_clave"] != fila(billetera, "dario")["hash_clave"], "Cada hash lleva su propia sal"


def test_rechaza_claves_debiles(cliente):
    for debil in ("123456", "corta1", "password1234", "contraseña123"):
        r = cliente.post("/api/registro", json={"usuario": "eva", "clave": debil, "documento": "1"})
        assert r.status_code == 400, f"«{debil}» no debería aceptarse (mínimo 12 caracteres y no estar en la lista de comunes)"


def test_clave_larga_con_espacios_se_acepta(cliente):
    r = cliente.post("/api/registro", json={"usuario": "fabio", "clave": "una frase larga es buena clave", "documento": "1"})
    assert r.status_code == 201, "Las frases con espacios deben aceptarse (ASVS no exige símbolos)"
    entrar(cliente, "fabio", "una frase larga es buena clave")
