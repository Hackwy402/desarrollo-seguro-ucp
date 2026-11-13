"""A10 · Condiciones excepcionales: si no se pudo cobrar, no se entrega."""
import sqlite3

from conftest import ANA


def test_pasarela_caida_no_deja_pagado(cliente, tienda, monkeypatch):
    def caida(*_):
        raise TimeoutError("la pasarela no respondió")

    monkeypatch.setattr(tienda.pasarela, "cobrar", caida)
    r = cliente.post("/carrito/checkout", json={"items": [{"id": 1, "cantidad": 1, "precio": 250000}]}, headers=ANA)
    assert r.status_code == 503, "Si no se sabe si se cobró, el pedido no puede quedar pagado"
    con = sqlite3.connect(tienda.DB)
    estados = [e for (e,) in con.execute("SELECT estado FROM pedidos WHERE usuario='ana' AND id > 2")]
    assert "pagado" not in estados


def test_error_sin_traza(cliente, tienda, monkeypatch):
    def explota(*_):
        raise RuntimeError("detalle interno: conexión a 10.0.0.12:5432")

    monkeypatch.setattr(tienda.pasarela, "cobrar", explota)
    tienda.app.config["PROPAGATE_EXCEPTIONS"] = False
    r = cliente.post("/carrito/checkout", json={"items": [{"id": 1, "cantidad": 1, "precio": 250000}]}, headers=ANA)
    assert "10.0.0.12" not in r.get_data(as_text=True)
    assert r.status_code >= 500
