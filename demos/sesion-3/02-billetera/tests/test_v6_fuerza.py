"""V6 · Fuerza bruta y enumeración: misma respuesta y límite de intentos."""
from conftest import entrar


def login(cliente, usuario, clave):
    return cliente.post("/api/login", json={"usuario": usuario, "clave": clave})


def test_misma_respuesta_si_el_usuario_no_existe(cliente):
    a = login(cliente, "ana", "no-es-la-clave")
    b = login(cliente, "nadie-se-llama-asi", "no-es-la-clave")
    assert a.status_code == b.status_code == 401, "Ambos casos: 401"
    assert a.get_json() == b.get_json(), "El mensaje no debe revelar si el usuario existe"


def test_bloqueo_tras_cinco_fallos(cliente):
    for _ in range(5):
        login(cliente, "ana", "intento-fallido")
    r = login(cliente, "ana", "Cafetal-de-Risaralda-2026")
    assert r.status_code == 429, "Tras 5 fallos seguidos, incluso la clave correcta recibe 429 por un tiempo"


def test_el_bloqueo_es_por_usuario(cliente):
    for _ in range(5):
        login(cliente, "ana", "intento-fallido")
    entrar(cliente, "beto")


def test_un_acierto_reinicia_el_contador(cliente):
    for _ in range(4):
        login(cliente, "beto", "intento-fallido")
    entrar(cliente, "beto")
    for _ in range(4):
        login(cliente, "beto", "intento-fallido")
    entrar(cliente, "beto")
