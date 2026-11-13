"""Esquema y datos de ejemplo de la Tienda UCP (SQLite)."""
import sqlite3

ESQUEMA = """
CREATE TABLE productos (id INTEGER PRIMARY KEY, nombre TEXT, precio INTEGER, visible INTEGER);
CREATE TABLE usuarios  (id INTEGER PRIMARY KEY, usuario TEXT, rol TEXT, hash_clave TEXT);
CREATE TABLE pedidos   (id INTEGER PRIMARY KEY, usuario TEXT, total INTEGER, estado TEXT, direccion TEXT);
CREATE TABLE resenas   (id INTEGER PRIMARY KEY, producto_id INTEGER, autor TEXT, texto TEXT);
CREATE TABLE cupones   (codigo TEXT PRIMARY KEY, descuento REAL, usuario TEXT, usado INTEGER);
"""

DATOS = """
INSERT INTO productos VALUES (1, 'Teclado mecánico', 250000, 1), (2, 'Mouse inalámbrico', 90000, 1),
  (3, 'Monitor 27 pulgadas', 1100000, 1), (4, 'Cable USB-C', 25000, 1), (5, 'Café D''Origen 500 g', 38000, 1),
  (99, 'Portátil de exhibición (precio interno)', 1, 0);
INSERT INTO usuarios VALUES (1, 'ana', 'cliente', '$argon2id$v=19$m=19456,t=2,p=1$ZGVtbw$ana'),
  (2, 'beto', 'cliente', '$argon2id$v=19$m=19456,t=2,p=1$ZGVtbw$beto'),
  (3, 'admin', 'admin', '$argon2id$v=19$m=19456,t=2,p=1$ZGVtbw$admin');
INSERT INTO pedidos VALUES (1, 'ana', 340000, 'pagado', 'Cra 1 # 2-3, Pereira'),
  (2, 'beto', 1100000, 'pagado', 'Calle 20 # 8-15, Dosquebradas');
INSERT INTO resenas VALUES (1, 1, 'ana', 'Excelente, las teclas se sienten muy bien.');
INSERT INTO cupones VALUES ('BIENVENIDA-ANA', 0.5, 'ana', 0), ('BIENVENIDA-BETO', 0.5, 'beto', 0);
"""


def crear(ruta):
    con = sqlite3.connect(ruta)
    con.executescript(ESQUEMA + DATOS)
    con.commit()
    con.close()
