"""V11 · Cifrado autenticado (AES-GCM), nonce aleatorio y llave fuera del código."""
import base64

import pytest
from cryptography.exceptions import InvalidTag

from conftest import fila


def test_ida_y_vuelta(billetera):
    assert billetera.descifrar(billetera.cifrar("1088123456", "ana"), "ana") == "1088123456"


def test_mismo_texto_distinto_cifrado(billetera):
    assert billetera.cifrar("1088123456", "ana") != billetera.cifrar("1088123456", "ana"), \
        "Con ECB el mismo dato da el mismo cifrado. Use AES-GCM con un nonce aleatorio por mensaje"


def test_detecta_manipulacion(billetera):
    blob = bytearray(base64.b64decode(billetera.cifrar("1088123456", "ana")))
    blob[-1] ^= 1
    with pytest.raises(InvalidTag):  # cifrado autenticado: AES-GCM o ChaCha20-Poly1305
        billetera.descifrar(base64.b64encode(bytes(blob)).decode(), "ana")


def test_no_se_puede_copiar_a_otro_usuario(billetera):
    with pytest.raises(InvalidTag):  # el usuario va como dato asociado (AAD)
        billetera.descifrar(billetera.cifrar("1088123456", "ana"), "beto")


def test_documento_no_queda_en_claro(cliente, billetera):
    cliente.get("/salud")
    cliente.post("/api/registro", json={"usuario": "gina", "clave": "otra frase larga y propia", "documento": "1110555444"})
    assert "1110555444" not in fila(billetera, "gina")["documento"]


def test_llave_no_esta_en_el_codigo(billetera):
    assert billetera.LLAVE_DATOS != b"billetera-ucp-llave-de-32-bytes!", "La llave viene del entorno o de un gestor de secretos"
    assert len(billetera.LLAVE_DATOS) == 32
