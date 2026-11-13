"""Carga la app indicada en APP_FILE (por defecto ../app.py) con una base de datos nueva por prueba."""
import base64
import importlib.util
import json
import os
import sqlite3
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

CLAVES = {"ana": "Cafetal-de-Risaralda-2026", "beto": "Nevado-del-Ruiz-5321m"}


def cargar_app():
    ruta = os.environ.get("APP_FILE", os.path.join(RAIZ, "app.py"))
    spec = importlib.util.spec_from_file_location("billetera_app", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture
def billetera(tmp_path):
    modulo = cargar_app()
    modulo.DB = str(tmp_path / "billetera.db")
    modulo.app.config["TESTING"] = True
    return modulo


@pytest.fixture
def cliente(billetera):
    return billetera.app.test_client()


def entrar(cliente, usuario, clave=None):
    r = cliente.post("/api/login", json={"usuario": usuario, "clave": clave or CLAVES[usuario]})
    assert r.status_code == 200, f"El login de {usuario} con su clave correcta debe funcionar"
    return {"Authorization": f"Bearer {r.json['token']}"}


def fila(billetera, usuario):
    con = sqlite3.connect(billetera.DB)
    con.row_factory = sqlite3.Row
    f = con.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,)).fetchone()
    con.close()
    return dict(f)


def b64(d):
    return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
