# bot/product_loader.py
"""
Compatibilidad con código legado.

Delegamos todo al nuevo loader (bot.loader) para que la fuente de verdad
sea siempre data/products.csv. Si algún endpoint antiguo llama a estas
funciones, no se rompe nada.
"""

from typing import List, Dict
from bot.loader import load_products

def load_products_from_csv(path: str = None) -> List[Dict]:
    """
    Ignora 'path' y usa el CSV oficial en data/products.csv
    (vía bot.loader.load_products).
    """
    df = load_products()
    return df.to_dict(orient="records")

def get_products() -> List[Dict]:
    """
    Devuelve los productos leídos desde data/products.csv.
    """
    df = load_products()
    return df.to_dict(orient="records")