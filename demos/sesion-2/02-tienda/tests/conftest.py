"""Carga la app indicada en APP_FILE (por defecto ../app.py) con una base de datos nueva por prueba."""
import importlib.util
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)


def cargar_app():
    ruta = os.environ.get("APP_FILE", os.path.join(RAIZ, "app.py"))
    spec = importlib.util.spec_from_file_location("tienda_app", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture
def tienda(tmp_path, monkeypatch):
    monkeypatch.delenv("PASARELA", raising=False)
    modulo = cargar_app()
    modulo.DB = str(tmp_path / "tienda.db")
    modulo.REPORTES = str(tmp_path / "reportes")
    modulo.app.config["TESTING"] = True
    return modulo


@pytest.fixture
def cliente(tienda):
    return tienda.app.test_client()


ANA = {"Authorization": "Bearer token-ana"}
BETO = {"Authorization": "Bearer token-beto"}
