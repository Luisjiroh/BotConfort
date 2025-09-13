# bot/classifier.py
"""
Clasificador simplificado:
- Delega TODA la lógica a bot.dialogue.manejar_dialogo
  (frío → tibio → caliente → cierre).
- Mantiene la firma para compatibilidad con imports antiguos.
"""

from typing import Tuple, Dict
from bot.dialogue import manejar_dialogo

def clasificar_mensaje(mensaje: str, state: Dict) -> Tuple[Dict, str, str]:
    # Simplemente delega al flujo conversacional completo
    new_state, clasificacion, respuesta = manejar_dialogo(mensaje, state or {})
    # Para compatibilidad: añade 'nivel' si alguien lo usa
    new_state["nivel"] = clasificacion
    return new_state, clasificacion, respuesta