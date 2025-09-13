"""
bot package initializer (simple y sin ciclos)

Expone:
- clasificar_mensaje  -> bot.dialogue.manejar_dialogo
- manejar_dialogo     -> bot.dialogue.manejar_dialogo
- get_products        -> productos desde bot.loader (por si algún endpoint lo usa)
- get_respuestas      -> diccionarios de data (si existen)
"""

from typing import Any, Tuple, Dict

# Flujo principal: frío -> tibio -> caliente -> cierre
from bot.dialogue import manejar_dialogo as _manejar_dialogo

# Lectura de productos desde CSV
from bot.loader import load_products as _load_products


def clasificar_mensaje(mensaje: str, state: dict):
    """Compat: la API puede seguir llamando 'clasificar_mensaje'."""
    return _manejar_dialogo(mensaje, state)

def manejar_dialogo(mensaje: str, state: dict):
    """Acceso directo."""
    return _manejar_dialogo(mensaje, state)

def get_products() -> list:
    """Devuelve lista de productos (dicts) desde el CSV."""
    df = _load_products()
    return df.to_dict(orient="records")

def get_respuestas() -> Tuple[Dict, Dict, Dict]:
    """
    Devuelve (respuestas_caliente, respuestas_tibio, respuestas_frio) si existen.
    Mantiene compatibilidad si algún módulo lo usa.
    """
    try:
        from bot import data
        caliente = getattr(data, "respuestas_caliente", {})
        tibio = getattr(data, "respuestas_tibio", {})
        frio = getattr(data, "respuestas_frio", {})
        return caliente, tibio, frio
    except Exception:
        return {}, {}, {}

__all__ = ["clasificar_mensaje", "manejar_dialogo", "get_products", "get_respuestas"]