"""A06 · Diseño inseguro: el servidor decide precios, cantidades y cupones."""
from conftest import ANA, BETO

# Precios de catálogo: el frontend oficial los envía junto con el id y la cantidad.
PRECIO = {1: 250000, 2: 90000, 3: 1100000, 99: 1}


def checkout(cliente, items, cupon=None, quien=ANA):
    cuerpo = {"items": [{"precio": PRECIO[i["id"]], **i} for i in items]}
    if cupon:
        cuerpo["cupon"] = cupon
    return cliente.post("/carrito/checkout", json=cuerpo, headers=quien)


def test_compra_normal(cliente):
    r = checkout(cliente, [{"id": 2, "cantidad": 2}])
    assert r.status_code == 201 and r.json["total"] == 180000 and r.json["estado"] == "pagado"


def test_precio_lo_pone_el_servidor(cliente):
    r = checkout(cliente, [{"id": 3, "cantidad": 1, "precio": 1}])
    assert r.status_code == 201 and r.json["total"] == 1100000, "Se usó el precio enviado por el cliente"


def test_cantidad_negativa(cliente):
    r = checkout(cliente, [{"id": 1, "cantidad": 1}, {"id": 3, "cantidad": -1}])
    assert r.status_code == 400


def test_producto_oculto_no_se_vende(cliente):
    assert checkout(cliente, [{"id": 99, "cantidad": 1}]).status_code == 400


def test_cupon_una_sola_vez(cliente):
    primero = checkout(cliente, [{"id": 1, "cantidad": 1}], "BIENVENIDA-ANA")
    assert primero.status_code == 201 and primero.json["total"] == 125000
    segundo = checkout(cliente, [{"id": 1, "cantidad": 1}], "BIENVENIDA-ANA")
    assert segundo.status_code == 400, "El cupón de un solo uso se aplicó dos veces"


def test_cupon_ajeno(cliente):
    r = checkout(cliente, [{"id": 1, "cantidad": 1}], "BIENVENIDA-ANA", quien=BETO)
    assert r.status_code == 400
