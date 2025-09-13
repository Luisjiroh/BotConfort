# api/state_manager.py
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "bot_state.db"

_conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
_cursor = _conn.cursor()
_cursor.execute("""
CREATE TABLE IF NOT EXISTS states (
    user_id TEXT PRIMARY KEY,
    state_json TEXT
)
""")
_conn.commit()

# Estado por defecto completo (alineado con bot.dialogue)
DEFAULT_STATE = {
    "fase": "frio",      # fase conversacional
    "nivel": None,       # compat si alguien lo usa

    # Datos de producto/cierre
    "producto": None,
    "precio": None,
    "color": None,
    "talla": None,

    # Datos del cliente
    "nombre": None,
    "telefono": None,
    "direccion": None,
    "ciudad": None,
}

def _merge_defaults(state: dict) -> dict:
    """
    Fusiona el estado recuperado con DEFAULT_STATE para garantizar
    que todas las llaves existan, sin perder lo ya guardado.
    """
    merged = DEFAULT_STATE.copy()
    if isinstance(state, dict):
        merged.update(state)
    return merged

def get_state(user_id: str) -> dict:
    cur = _conn.cursor()
    cur.execute("SELECT state_json FROM states WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        try:
            current = json.loads(row[0])
            return _merge_defaults(current)
        except Exception:
            pass
    # si no existe o falló la carga, crea por defecto
    save_state(user_id, DEFAULT_STATE.copy())
    return DEFAULT_STATE.copy()

def save_state(user_id: str, state: dict):
    s = json.dumps(_merge_defaults(state), ensure_ascii=False)
    cur = _conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO states(user_id, state_json) VALUES(?, ?)",
        (user_id, s)
    )
    _conn.commit()

def reset_state(user_id: str):
    save_state(user_id, DEFAULT_STATE.copy())
    return DEFAULT_STATE.copy()