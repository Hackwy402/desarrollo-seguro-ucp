"""Esquema y datos de ejemplo de la Billetera UCP (SQLite).

La función crear() recibe el hash de contraseñas y el cifrado de la app que la llama:
así la base de datos de prueba usa siempre los controles que ustedes construyan.
"""
import sqlite3

ESQUEMA = """
CREATE TABLE usuarios (usuario TEXT PRIMARY KEY, nombre TEXT, correo TEXT, rol TEXT,
                       hash_clave TEXT, documento TEXT, saldo INTEGER);
CREATE TABLE cuentas (id INTEGER PRIMARY KEY, usuario TEXT);
CREATE TABLE movimientos (id INTEGER PRIMARY KEY, cuenta_id INTEGER, valor INTEGER, concepto TEXT);
"""

USUARIOS = [
    # usuario, nombre, correo, rol, clave, documento, saldo
    ("ana", "Ana Gómez", "ana@billetera.test", "cliente", "Cafetal-de-Risaralda-2026", "1088123456", 1250000),
    ("beto", "Beto Ríos", "beto@billetera.test", "cliente", "Nevado-del-Ruiz-5321m", "1093765432", 830000),
    ("admin", "Administración", "admin@billetera.test", "admin", "Admin-solo-de-laboratorio-42", "900123456", 0),
]


def crear(ruta, hashear, cifrar):
    con = sqlite3.connect(ruta)
    con.executescript(ESQUEMA)
    for u, nombre, correo, rol, clave, doc, saldo in USUARIOS:
        con.execute("INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (u, nombre, correo, rol, hashear(clave), cifrar(doc, u), saldo))
    con.execute("INSERT INTO cuentas VALUES (1, 'ana'), (2, 'beto')")
    con.executemany("INSERT INTO movimientos (cuenta_id, valor, concepto) VALUES (1, ?, ?)",
                    [(-(1000 + i * 37), f"Compra {i}") for i in range(250)])
    con.executemany("INSERT INTO movimientos (cuenta_id, valor, concepto) VALUES (2, ?, ?)",
                    [(500000, "Nómina"), (-120000, "Arriendo"), (-45000, "Mercado")])
    con.commit()
    con.close()
