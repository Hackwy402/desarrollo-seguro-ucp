"""V9 · JWT: firma verificada, algoritmo fijo, expiración corta, emisor y audiencia."""
import time

import jwt

from conftest import b64, entrar


def pedir(cliente, token):
    return cliente.get("/api/perfil", headers={"Authorization": f"Bearer {token}"})


def test_token_valido_funciona(cliente):
    assert cliente.get("/api/perfil", headers=entrar(cliente, "ana")).status_code == 200


def test_sin_firma_alg_none_rechazado(cliente):
    token = b64({"alg": "none", "typ": "JWT"}) + "." + b64({"sub": "admin", "exp": int(time.time()) + 600}) + "."
    assert pedir(cliente, token).status_code == 401, "alg=none jamás se acepta"


def test_firma_con_otro_secreto_rechazada(cliente):
    token = jwt.encode({"sub": "admin", "exp": int(time.time()) + 600}, "otro-secreto", algorithm="HS256")
    assert pedir(cliente, token).status_code == 401, "Verifique la firma"


def test_secreto_robusto_y_fuera_del_codigo(billetera, cliente):
    s = billetera.JWT_SECRETO
    s = s.encode() if isinstance(s, str) else s
    assert len(s) >= 32 and s != b"secreto", "Mínimo 32 bytes aleatorios, leídos del entorno"
    token = jwt.encode({"sub": "admin", "exp": int(time.time()) + 600}, "secreto", algorithm="HS256")
    assert pedir(cliente, token).status_code == 401


def test_token_expirado_rechazado(billetera, cliente):
    ahora = int(time.time())
    token = jwt.encode({"sub": "ana", "iss": billetera.JWT_EMISOR, "aud": billetera.JWT_AUDIENCIA,
                        "iat": ahora - 3600, "exp": ahora - 60}, billetera.JWT_SECRETO, algorithm="HS256")
    assert pedir(cliente, token).status_code == 401


def test_audiencia_ajena_rechazada(billetera, cliente):
    ahora = int(time.time())
    token = jwt.encode({"sub": "ana", "iss": billetera.JWT_EMISOR, "aud": "otra-api",
                        "iat": ahora, "exp": ahora + 600}, billetera.JWT_SECRETO, algorithm="HS256")
    assert pedir(cliente, token).status_code == 401, "Un token emitido para otra API no sirve aquí"


def test_token_emitido_expira_en_15_minutos_o_menos(cliente):
    token = entrar(cliente, "ana")["Authorization"].removeprefix("Bearer ")
    d = jwt.decode(token, options={"verify_signature": False})
    assert "exp" in d and "iat" in d, "El token lleva iat y exp"
    assert d["exp"] - d["iat"] <= 900
