"""Billetera UCP: API de una billetera digital. VERSIÓN INSEGURA, solo para el laboratorio.

Cada sección marcada con «KATA» tiene una falla real de autenticación, de APIs
(OWASP API Security Top 10:2023) o de criptografía. Su trabajo es construir el
control sin romper la funcionalidad: las pruebas de tests/ verifican ambas cosas.
Ejecutar:  bash katas.sh        (o  bash katas.sh v6_claves)

Usuarios de prueba (POST /api/login):
  ana / Cafetal-de-Risaralda-2026      beto / Nevado-del-Ruiz-5321m
"""
import base64
import datetime as dt
import hashlib
import os
import sqlite3

import jwt
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, g, jsonify, request

import datos

app = Flask(__name__)
app.json.ensure_ascii = False
DB = os.environ.get("DB_PATH", "/tmp/billetera.db")


def db():
    if "db" not in g:
        if not os.path.exists(DB):
            datos.crear(DB, hashear, cifrar)
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def cerrar(_):
    con = g.pop("db", None)
    if con:
        con.close()


@app.get("/salud")
def salud():
    return jsonify(estado="ok")


# ---------------------------------------------------------------------------
# KATA V6 · Almacenamiento de contraseñas
# MD5 sin sal: rápido de calcular y dos usuarios con la misma clave tienen el
# mismo hash. Además se acepta cualquier contraseña, incluso «123456».
# ---------------------------------------------------------------------------
def hashear(clave):
    return hashlib.md5(clave.encode()).hexdigest()


def verificar_clave(hash_guardado, clave):
    return hash_guardado == hashlib.md5(clave.encode()).hexdigest()


# ---------------------------------------------------------------------------
# KATA V11 · Criptografía de datos en reposo
# El documento de identidad se cifra con AES en modo ECB y una llave escrita en
# el código: el mismo documento produce siempre el mismo texto cifrado y nadie
# detecta si alguien lo altera en la base de datos.
# ---------------------------------------------------------------------------
LLAVE_DATOS = b"billetera-ucp-llave-de-32-bytes!"


def cifrar(texto, usuario):
    relleno = padding.PKCS7(128).padder()
    datos_rellenos = relleno.update(texto.encode()) + relleno.finalize()
    c = Cipher(algorithms.AES(LLAVE_DATOS), modes.ECB()).encryptor()
    return base64.b64encode(c.update(datos_rellenos) + c.finalize()).decode()


def descifrar(blob, usuario):
    d = Cipher(algorithms.AES(LLAVE_DATOS), modes.ECB()).decryptor()
    datos_rellenos = d.update(base64.b64decode(blob)) + d.finalize()
    quitar = padding.PKCS7(128).unpadder()
    return (quitar.update(datos_rellenos) + quitar.finalize()).decode()


# ---------------------------------------------------------------------------
# KATA V9 · Tokens JWT
# Secreto adivinable, sin expiración, y la verificación ni siquiera revisa la
# firma: cualquiera puede fabricar un token con el usuario que quiera.
# ---------------------------------------------------------------------------
JWT_SECRETO = "secreto"


def emitir_token(usuario):
    return jwt.encode({"sub": usuario}, JWT_SECRETO, algorithm="HS256")


def usuario_actual():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    try:
        datos_token = jwt.decode(token, options={"verify_signature": False})
    except jwt.PyJWTError:
        return None
    return datos_token.get("sub")


@app.post("/api/registro")
def registro():
    d = request.get_json(silent=True) or {}
    usuario, clave, documento = d.get("usuario", ""), d.get("clave", ""), d.get("documento", "")
    if not usuario or not clave:
        return jsonify(error="usuario y clave son obligatorios"), 400
    if db().execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,)).fetchone():
        return jsonify(error="el usuario ya existe"), 409
    db().execute("INSERT INTO usuarios VALUES (?, ?, ?, 'cliente', ?, ?, 0)",
                 (usuario, d.get("nombre", usuario), d.get("correo", ""), hashear(clave), cifrar(documento, usuario)))
    db().commit()
    return jsonify(estado="creado"), 201


# ---------------------------------------------------------------------------
# KATA V6 · Fuerza bruta y enumeración de usuarios
# Intentos ilimitados, y el mensaje de error le dice al atacante si el usuario
# existe o no.
# ---------------------------------------------------------------------------
@app.post("/api/login")
def login():
    d = request.get_json(silent=True) or {}
    usuario, clave = d.get("usuario", ""), d.get("clave", "")
    fila = db().execute("SELECT hash_clave FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
    if not fila:
        return jsonify(error="el usuario no existe"), 404
    if not verificar_clave(fila["hash_clave"], clave):
        return jsonify(error="contraseña incorrecta"), 401
    return jsonify(token=emitir_token(usuario))


# ---------------------------------------------------------------------------
# KATA API3 · Autorización a nivel de propiedad (asignación masiva y exposición)
# El perfil devuelve todas las columnas, incluido el hash; la actualización
# acepta cualquier campo que llegue en el JSON, también «rol» y «saldo».
# ---------------------------------------------------------------------------
@app.get("/api/perfil")
def ver_perfil():
    usuario = usuario_actual()
    if not usuario:
        return jsonify(error="no autenticado"), 401
    fila = db().execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
    if not fila:
        return jsonify(error="no encontrado"), 404
    return jsonify(dict(fila))


@app.patch("/api/perfil")
def editar_perfil():
    usuario = usuario_actual()
    if not usuario:
        return jsonify(error="no autenticado"), 401
    for campo, valor in (request.get_json(silent=True) or {}).items():
        db().execute(f"UPDATE usuarios SET {campo} = ? WHERE usuario = ?", (valor, usuario))
    db().commit()
    return ver_perfil()


# ---------------------------------------------------------------------------
# KATA API1 · Autorización a nivel de objeto (BOLA)
# KATA API4 · Consumo de recursos sin restricción
# Cualquier usuario autenticado lee los movimientos de cualquier cuenta, y
# «limite» acepta lo que sea: 100000, -1 (en SQLite, sin límite) o texto.
# ---------------------------------------------------------------------------
@app.get("/api/cuentas/<int:cid>/movimientos")
def movimientos(cid):
    if not usuario_actual():
        return jsonify(error="no autenticado"), 401
    limite = int(request.args.get("limite", 20))
    filas = db().execute(
        "SELECT id, valor, concepto FROM movimientos WHERE cuenta_id = ? ORDER BY id DESC LIMIT ?", (cid, limite)
    ).fetchall()
    return jsonify([dict(f) for f in filas])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("DEBUG", "0") == "1")
