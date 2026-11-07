"""API de facturas – versión SEGURA. Misma funcionalidad que app_insegura.py con los controles aplicados."""
import json
import logging
import os
import urllib.error
import urllib.request

from flask import Flask, abort, g, jsonify, request

log = logging.getLogger("facturas")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]  # sin valor por defecto: si falta, no arranca
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
ORIGENES_PERMITIDOS = {"https://app.ejemplo.co"}

PERMISOS_URL = os.environ.get("PERMISOS_URL", "http://permisos:8000")

USUARIOS = {"token-ana": {"id": 1, "nombre": "ana"}, "token-luis": {"id": 2, "nombre": "luis"}}
FACTURAS = {
    1: {"id": 1, "cliente_id": 1, "cliente": "ana", "total": 120000},
    2: {"id": 2, "cliente_id": 2, "cliente": "luis", "total": 980000},
    3: {"id": 3, "cliente_id": 2, "cliente": "luis", "total": 45000},
}


class PermisosNoDisponibles(Exception):
    pass


@app.before_request
def autenticar():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    g.usuario = USUARIOS.get(token)


@app.after_request
def cors(resp):
    origen = request.headers.get("Origin")
    if origen in ORIGENES_PERMITIDOS:
        resp.headers["Access-Control-Allow-Origin"] = origen
    return resp


@app.errorhandler(Exception)
def error_generico(e):
    code = getattr(e, "code", 500)
    if code == 500:
        log.exception("error no controlado")
    return jsonify({"error": "solicitud no procesada"}), code


def login_requerido(fn):
    def envoltura(*args, **kwargs):
        if g.usuario is None:
            abort(401)
        return fn(*args, **kwargs)

    envoltura.__name__ = fn.__name__
    return envoltura


def consultar_rol(usuario, doc_id):
    url = f"{PERMISOS_URL}/rol?usuario={usuario['id']}&doc={doc_id}"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return json.load(r)["rol"]
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
        raise PermisosNoDisponibles() from e


def puede_editar(usuario, doc_id):
    try:
        return consultar_rol(usuario, doc_id) == "editor"
    except PermisosNoDisponibles:
        log.warning("servicio de permisos no disponible; acceso negado")
        return False


@app.get("/facturas/<int:fid>")
@login_requerido
def ver_factura(fid):
    factura = FACTURAS.get(fid)
    if factura is None or factura["cliente_id"] != g.usuario["id"]:
        abort(404)  # 404 y no 403: no revela que la factura existe
    return jsonify(factura)


@app.post("/documentos/<int:doc_id>/editar")
@login_requerido
def editar_documento(doc_id):
    if not puede_editar(g.usuario, doc_id):
        abort(403)
    return jsonify({"documento": doc_id, "editado_por": g.usuario["nombre"]})


@app.get("/salud")
def salud():
    return jsonify({"estado": "ok"})


@app.get("/error")
def error():
    return 1 / 0


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
