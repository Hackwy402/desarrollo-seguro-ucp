"""Pasarela de pagos simulada. PASARELA=caida simula que no responde (timeout)."""
import os


class Rechazado(Exception):
    """La pasarela respondió y negó el cobro."""


def cobrar(usuario, monto):
    if os.environ.get("PASARELA") == "caida":
        raise TimeoutError("la pasarela no respondió en 5 s")
    if monto <= 0:
        raise Rechazado("monto inválido")
    return f"aprobado-{usuario}-{monto}"
