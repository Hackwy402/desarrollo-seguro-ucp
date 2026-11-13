"""Tienda UCP: API de una tienda en línea. VERSIÓN INSEGURA, solo para el laboratorio.

Cada sección marcada con «KATA» contiene una falla real del OWASP Top 10:2025.
Su trabajo es construir el control sin romper la funcionalidad: las pruebas de
tests/ verifican ambas cosas.  Ejecutar:  bash katas.sh   (o  bash katas.sh a05_sql)

Usuarios de prueba (cabecera Authorization: Bearer <token>):
  token-ana -> ana      token-beto -> beto
"""
import os
import sqlite3
import subprocess

from flask import Flask, g, jsonify, request

import datos
import pasarela

app = Flask(__name__)
app.json.ensure_ascii = False
DB = os.environ.get("DB_PATH", "/tmp/tienda.db")
REPORTES = os.environ.get("REPORTES_DIR", "/tmp/reportes")
TOKENS = {"token-ana": "ana", "token-beto": "beto"}


def db():
    if "db" not in g:
        if not os.path.exists(DB):
            datos.crear(DB)
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def cerrar(_):
    con = g.pop("db", None)
    if con:
        con.close()


def usuario_actual():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    return TOKENS.get(token)


@app.get("/salud")
def salud():
    return jsonify(estado="ok")


# ---------------------------------------------------------------------------
# KATA A02 · Configuración insegura
# CORS refleja cualquier origen y además permite credenciales; no hay cabeceras
# de seguridad. Cualquier sitio que visite un cliente puede leer sus pedidos.
# ---------------------------------------------------------------------------
@app.after_request
def cabeceras(resp):
    origen = request.headers.get("Origin")
    if origen:
        resp.headers["Access-Control-Allow-Origin"] = origen
        resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


# ---------------------------------------------------------------------------
# KATA A01 · Control de acceso roto (IDOR, como en la sesión 1)
# Verifica que haya sesión, pero no que el pedido sea de quien lo pide.
# ---------------------------------------------------------------------------
@app.get("/pedidos/<int:pid>")
def ver_pedido(pid):
    usuario = usuario_actual()
    if not usuario:
        return jsonify(error="no autenticado"), 401
    fila = db().execute(
        "SELECT id, usuario, total, estado, direccion FROM pedidos WHERE id = ?", (pid,)
    ).fetchone()
    if not fila:
        return jsonify(error="no encontrado"), 404
    return jsonify(dict(fila))


# ---------------------------------------------------------------------------
# KATA A05 · Inyección SQL
# La búsqueda arma la consulta pegando texto del usuario.
# ---------------------------------------------------------------------------
@app.get("/productos")
def buscar_productos():
    q = request.args.get("q", "")
    sql = f"SELECT id, nombre, precio FROM productos WHERE visible = 1 AND nombre LIKE '%{q}%'"
    filas = db().execute(sql).fetchall()
    return jsonify([dict(f) for f in filas])


# ---------------------------------------------------------------------------
# KATA A05 · Cross-site scripting (XSS) almacenado
# Las reseñas se insertan en el HTML tal como llegaron.
# ---------------------------------------------------------------------------
@app.post("/productos/<int:pid>/resenas")
def crear_resena(pid):
    usuario = usuario_actual()
    if not usuario:
        return jsonify(error="no autenticado"), 401
    texto = (request.get_json(silent=True) or {}).get("texto", "")
    db().execute("INSERT INTO resenas (producto_id, autor, texto) VALUES (?, ?, ?)", (pid, usuario, texto))
    db().commit()
    return jsonify(estado="creada"), 201


@app.get("/productos/<int:pid>/resenas")
def ver_resenas(pid):
    filas = db().execute("SELECT autor, texto FROM resenas WHERE producto_id = ?", (pid,)).fetchall()
    items = "".join(f"<li><b>{f['autor']}</b>: {f['texto']}</li>" for f in filas)
    return f"<!doctype html><title>Reseñas</title><h1>Reseñas</h1><ul>{items}</ul>"


# ---------------------------------------------------------------------------
# KATA A05 · Inyección de comandos del sistema operativo
# El nombre del reporte termina dentro de una línea de shell.
# ---------------------------------------------------------------------------
@app.post("/reportes")
def generar_reporte():
    if not usuario_actual():
        return jsonify(error="no autenticado"), 401
    nombre = (request.get_json(silent=True) or {}).get("nombre", "ventas")
    os.makedirs(REPORTES, exist_ok=True)
    with open(os.path.join(REPORTES, "ventas.csv"), "w") as f:
        f.write("pedido,total\n1,340000\n2,1100000\n")
    cmd = f"cd {REPORTES} && tar czf {nombre}.tgz ventas.csv"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify(archivo=f"{nombre}.tgz", salida=r.stdout + r.stderr)


# ---------------------------------------------------------------------------
# KATA A06 · Diseño inseguro (lógica de negocio)
# El servidor confía en el precio y la cantidad que envía el cliente, y el
# cupón de bienvenida se puede usar muchas veces y por cualquier usuario.
# KATA A10 · Manejo inadecuado de condiciones excepcionales
# Si la pasarela no responde, el pedido queda «pagado» (falla abierta).
# ---------------------------------------------------------------------------
@app.post("/carrito/checkout")
def checkout():
    usuario = usuario_actual()
    if not usuario:
        return jsonify(error="no autenticado"), 401
    datos_req = request.get_json(silent=True) or {}
    total = 0
    for item in datos_req.get("items", []):
        total += item["precio"] * item["cantidad"]

    cupon = datos_req.get("cupon")
    if cupon:
        fila = db().execute("SELECT descuento FROM cupones WHERE codigo = ?", (cupon,)).fetchone()
        if fila:
            total = int(total * (1 - fila["descuento"]))

    estado = "pagado"
    try:
        pasarela.cobrar(usuario, total)
    except pasarela.Rechazado:
        estado = "rechazado"
    except Exception as e:  # «que una caída de la pasarela no nos haga perder la venta»
        app.logger.warning("pasarela con problemas: %s", e)

    cur = db().execute(
        "INSERT INTO pedidos (usuario, total, estado, direccion) VALUES (?, ?, ?, '')", (usuario, total, estado)
    )
    db().commit()
    return jsonify(pedido=cur.lastrowid, total=total, estado=estado), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("DEBUG", "1") == "1")
