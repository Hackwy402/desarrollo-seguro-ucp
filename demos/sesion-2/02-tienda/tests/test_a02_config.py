"""A02 · Configuración segura: CORS restringido y cabeceras de seguridad."""
from conftest import ANA

PROPIO = "http://127.0.0.1:5003"


def test_cors_no_refleja_origen_ajeno(cliente):
    r = cliente.get("/pedidos/1", headers={**ANA, "Origin": "https://atacante.example"})
    assert r.headers.get("Access-Control-Allow-Origin") != "https://atacante.example"


def test_cors_permite_el_frontend_propio(cliente):
    r = cliente.get("/pedidos/1", headers={**ANA, "Origin": PROPIO})
    assert r.headers.get("Access-Control-Allow-Origin") == PROPIO


def test_cabeceras_de_seguridad(cliente):
    h = cliente.get("/salud").headers
    assert h.get("X-Content-Type-Options") == "nosniff"
    assert "frame-ancestors" in h.get("Content-Security-Policy", "") or h.get("X-Frame-Options")


def test_debug_apagado_por_defecto(tienda, monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    import inspect
    fuente = inspect.getsource(tienda)
    assert 'get("DEBUG", "1")' not in fuente, "El modo depuración no puede estar encendido por defecto"
