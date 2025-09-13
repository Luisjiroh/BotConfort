# api/app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import shutil

from api.state_manager import get_state, save_state, reset_state
from bot import clasificar_mensaje, get_products   # wrappers de bot/__init__.py
from bot.loader import load_products               # fuente de verdad CSV

# === Paths base ===
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

INDEX_HTML = BASE_DIR / "web" / "index.html"
STATIC_DIR = BASE_DIR / "web" / "static"

app = FastAPI(title="Sales Bot API")

# Montar /static solo si existe
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ===== Modelos =====
class ChatMessage(BaseModel):
    user_id: str
    mensaje: str

# ===== Rutas Web =====
@app.get("/", include_in_schema=False)
def root_redirect():
    # Redirige a /web para abrir el chat
    return RedirectResponse(url="/web")

@app.get("/web", include_in_schema=False)
def web():
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    return JSONResponse({"error": "No se encontró web/index.html"}, status_code=404)

# ===== API =====
@app.post("/chat")
def chat(msg: ChatMessage):
    state = get_state(msg.user_id)
    new_state, clasificacion, respuesta = clasificar_mensaje(msg.mensaje, state)
    save_state(msg.user_id, new_state)
    return {"clasificacion": clasificacion, "respuesta": respuesta, "estado": new_state}

@app.get("/products")
def products():
    # Devuelve productos desde el CSV
    try:
        df = load_products()
        return df.to_dict(orient="records")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/admin/reset/{user_id}")
def reset(user_id: str):
    s = reset_state(user_id)
    return {"ok": True, "estado": s}

@app.post("/admin/upload-products")
async def upload_products(file: UploadFile = File(...)):
    """
    Sube un CSV y lo guarda como data/products.csv (sobrescribe).
    Luego valida cargándolo con bot.loader.load_products().
    """
    dest = DATA_DIR / "products.csv"
    try:
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        file.file.close()

    try:
        df = load_products()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error cargando CSV: {e}")

    return {"ok": True, "count": len(df)}