# api/app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import shutil

from api.state_manager import get_state, save_state, reset_state
from bot import clasificar_mensaje, get_products  # usa nuestro __init__ nuevo
from bot.loader import load_products  # fuente de verdad del CSV

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Sales Bot API")

# ===== WEB (templates/estáticos son opcionales) =====
templates_dir = BASE_DIR / "web" / "templates"
static_dir = BASE_DIR / "web" / "static"
index_file = BASE_DIR / "web" / "index.html"

# Monta /static solo si existe
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ========================
# 📌 MODELOS
# ========================
class ChatMessage(BaseModel):
    user_id: str
    mensaje: str

# ========================
# 📌 RUTAS API
# ========================
@app.post("/chat")
async def chat(msg: ChatMessage):
    state = get_state(msg.user_id)
    new_state, clasificacion, respuesta = clasificar_mensaje(msg.mensaje, state)
    save_state(msg.user_id, new_state)
    return {"clasificacion": clasificacion, "respuesta": respuesta, "estado": new_state}

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

@app.get("/products")
def products():
    try:
        return get_products()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/admin/reset/{user_id}")
def reset_user(user_id: str):
    s = reset_state(user_id)
    return {"ok": True, "estado": s}
# api/app.py
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path

from api.state_manager import get_state, save_state, reset_state
from bot import clasificar_mensaje
from bot.loader import load_products

BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_HTML = BASE_DIR / "web" / "index.html"

app = FastAPI(title="Sales Bot API")

class ChatMessage(BaseModel):
    user_id: str
    mensaje: str

@app.get("/")
def root():
    return {"ok": True, "msg": "Usa /web para abrir el chat o /docs para probar la API."}

@app.get("/web")
def web():
    if INDEX_HTML.exists():
        return FileResponse(str(INDEX_HTML))
    return JSONResponse({"error": "No se encontró web/index.html"}, status_code=404)

@app.post("/chat")
def chat(msg: ChatMessage):
    state = get_state(msg.user_id)
    new_state, clasificacion, respuesta = clasificar_mensaje(msg.mensaje, state)
    save_state(msg.user_id, new_state)
    return {"clasificacion": clasificacion, "respuesta": respuesta, "estado": new_state}

@app.get("/products")
def products():
    try:
        df = load_products()
        return df.to_dict(orient="records")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/admin/reset/{user_id}")
def reset(user_id: str):
    s = reset_state(user_id)
    return {"ok": True, "estado": s}