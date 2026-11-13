"""A05 · Inyección SQL en la búsqueda de productos."""


def nombres(r):
    return [p["nombre"] for p in r.json]


def test_busqueda_normal(cliente):
    r = cliente.get("/productos?q=Teclado")
    assert r.status_code == 200 and nombres(r) == ["Teclado mecánico"]


def test_busqueda_con_apostrofo(cliente):
    r = cliente.get("/productos?q=D'Origen")
    assert r.status_code == 200, "Un nombre con apóstrofo es una búsqueda legítima"
    assert nombres(r) == ["Café D'Origen 500 g"]


def test_or_1_1_no_revela_ocultos(cliente):
    r = cliente.get("/productos?q=' OR 1=1 --")
    assert r.status_code == 200
    assert "Portátil de exhibición (precio interno)" not in nombres(r)


def test_union_no_extrae_usuarios(cliente):
    r = cliente.get("/productos?q=' UNION SELECT id, usuario || ':' || hash_clave, 0 FROM usuarios --")
    texto = r.get_data(as_text=True)
    assert "argon2id" not in texto and "admin" not in texto
