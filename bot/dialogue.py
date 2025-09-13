# bot/dialogue.py
import re
from bot.data import respuestas_frio  # saludos/rompehielos (frío)
from bot.loader import find_product_by_name, build_price_message

COLORS = ["negro", "azul", "marron", "marrón"]
TALLA_RE = re.compile(r"\b(37|38|39|40|41|42|43)\b")
TEL_RE = re.compile(r"\b\d{7,10}\b")

def _fmt_price(v: int) -> str:
    return f"${v:,}".replace(",", ".")

def _missing_fields(state: dict):
    order = ["producto", "color", "talla", "nombre", "telefono", "direccion", "ciudad"]
    return [k for k in order if not state.get(k)]

def _ask_for_next_missing(state: dict) -> str:
    faltantes = _missing_fields(state)
    if not faltantes:
        precio = _fmt_price(state.get("precio", 0))
        return (
            f"📦 Sr. {state['nombre']}, este es su pedido:\n"
            f"Producto: {state['producto']}\n"
            f"Color: {state['color']}\n"
            f"Talla: {state['talla']}\n"
            f"Precio: {precio}\n"
            f"Entrega: {state['direccion']}, {state['ciudad']}\n"
            f"Tel: {state['telefono']}\n\n"
            f"Por favor revise y si está bien nos confirma para despacharlo. ✅"
        )
    nxt = faltantes[0]
    if nxt == "producto":
        return build_price_message()
    if nxt == "color":
        return "¿Qué color prefieres? (negro, azul o marrón)"
    if nxt == "talla":
        return "Perfecto. ¿Qué talla usas? (37–43)"
    if nxt == "nombre":
        return "¿Cuál es tu nombre?"
    if nxt == "telefono":
        return "📞 ¿Cuál es tu número de teléfono? (7 a 10 dígitos)"
    if nxt == "direccion":
        return "📍 Indícame la dirección de entrega."
    if nxt == "ciudad":
        return "¿En qué ciudad recibirás tu pedido?"
    return "¿Podrías confirmar el dato pendiente?"

def _try_capture_product(mensaje: str, state: dict):
    prod = find_product_by_name(mensaje)
    if not prod:
        return None
    if isinstance(prod, list):
        nombres = ", ".join([p["Nombre"] for p in prod if p.get("Nombre")])
        return f"He encontrado varias opciones: {nombres}. ¿Cuál prefieres?"
    state["producto"] = prod["Nombre"]
    try:
        state["precio"] = int(prod["Precio"])
    except Exception:
        state["precio"] = 0
    return (f"Perfecto 🙌. Has elegido **{state['producto']}**. "
            f"Está hoy en oferta y te queda en {_fmt_price(state['precio'])}. "
            f"Puedes decirme el color o la talla para continuar.")

def _try_capture_color(mensaje: str, state: dict):
    for c in COLORS:
        if c in mensaje:
            state["color"] = "marrón" if c in ("marron", "marrón") else c
            if not state.get("talla"):
                return f"Color {state['color']} anotado 🎨. ¿Cuál es tu talla (37–43)?"
            return "✅ Súper. ¿Cuál es tu nombre?"
    return None

def _try_capture_talla(mensaje: str, state: dict):
    m = TALLA_RE.search(mensaje)
    if m:
        state["talla"] = m.group(1)
        if state.get("color"):
            return "✅ Súper. ¿Cuál es tu nombre?"
        else:
            return "✅ Súper. ¿Qué color prefieres? (negro, azul o marrón)"
    return None

def _try_capture_nombre(mensaje: str, state: dict):
    state["nombre"] = mensaje.title()
    return f"Gracias {state['nombre']} 🙌. 📞 ¿Cuál es tu número de teléfono? (7 a 10 dígitos)"

def _try_capture_telefono(mensaje: str, state: dict):
    m = TEL_RE.search(mensaje)
    if m:
        state["telefono"] = m.group(0)
        return "Perfecto. 📍 Indícame tu dirección de entrega."
    return "Por favor envíame un número de teléfono válido (7 a 10 dígitos)."

def _try_capture_direccion(mensaje: str, state: dict):
    state["direccion"] = mensaje.strip()
    return "¿En qué ciudad recibirás tu pedido?"

def _try_capture_ciudad(mensaje: str, state: dict):
    state["ciudad"] = mensaje.title()
    precio = _fmt_price(state.get("precio", 0))
    return (
        f"📦 Sr. {state['nombre']}, este es su pedido:\n"
        f"Producto: {state['producto']}\n"
        f"Color: {state['color']}\n"
        f"Talla: {state['talla']}\n"
        f"Precio: {precio}\n"
        f"Entrega: {state['direccion']}, {state['ciudad']}\n"
        f"Tel: {state['telefono']}\n\n"
        f"Por favor revise y si está bien nos confirma para despacharlo. ✅"
    )

def manejar_dialogo(mensaje: str, state: dict):
    mensaje = (mensaje or "").strip().lower()
    if not state:
        state = {"fase": "frio"}

    # 0) Si dice "precio/valor/costo", limpiamos y mostramos modelos (pasa a CALIENTE)
    if any(p in mensaje for p in ["precio", "valor", "cuánto vale", "cuanto vale", "coste", "costo", "oferta", "promoción", "promocion"]):
        state["fase"] = "caliente"
        for k in ("producto", "precio", "color", "talla", "nombre", "telefono", "direccion", "ciudad"):
            state.pop(k, None)
        return state, "Caliente", build_price_message()

    # 1) FRÍO → usar respuestas_frio y pasar a TIBIO (NO empujar a precio automáticamente)
    if state["fase"] == "frio":
        for k, r in respuestas_frio.items():
            if (isinstance(k, tuple) and any(word in mensaje for word in k)) or (isinstance(k, str) and k in mensaje):
                state["fase"] = "tibio"
                return state, "Frio", r
        # sin saludo claro
        return state, "Frio", "¡Hola! 👋 ¿Quieres ver los modelos o saber los precios? Puedes escribir “precio” o decirme qué modelo te interesa."

    # 2) TIBIO → si pide precio, mostrar; si menciona producto, tomar; si no, guiar
    if state["fase"] == "tibio":
        # precio en tibio
        if any(p in mensaje for p in ["precio", "valor", "cuánto vale", "cuanto vale", "coste", "costo", "oferta", "promoción", "promocion"]):
            state["fase"] = "caliente"
            for k in ("producto", "precio", "color", "talla", "nombre", "telefono", "direccion", "ciudad"):
                state.pop(k, None)
            return state, "Caliente", build_price_message()

        # intentar captar producto
        picked = _try_capture_product(mensaje, state)
        if picked:
            state["fase"] = "caliente"
            return state, "Tibio", picked

        # no hay producto aún
        return state, "Tibio", "¿Prefieres que te muestre precios (escribe “precio”) o ya tienes un modelo en mente (por ejemplo: “titanium”, “casual”)?"

    # 3) CALIENTE: color/talla en cualquier orden → nombre → teléfono → dirección → ciudad → confirmación
    if state["fase"] == "caliente":
        # si no hay producto aún, intentar capturar
        if not state.get("producto"):
            picked = _try_capture_product(mensaje, state)
            if picked:
                return state, "Caliente", picked
            return state, "Caliente", build_price_message()

        # color/talla
        if not state.get("color") or not state.get("talla"):
            if not state.get("talla"):
                out_talla = _try_capture_talla(mensaje, state)
                if out_talla:
                    return state, "Caliente", out_talla
            if not state.get("color"):
                out_color = _try_capture_color(mensaje, state)
                if out_color:
                    return state, "Caliente", out_color
            # guiar
            falt = _missing_fields(state)
            if "color" in falt:
                return state, "Caliente", "¿Qué color prefieres? (negro, azul o marrón)"
            return state, "Caliente", "¿Cuál es tu talla (37–43)?"

        # nombre
        if not state.get("nombre"):
            return state, "Caliente", _try_capture_nombre(mensaje, state)
        # teléfono
        if not state.get("telefono"):
            return state, "Caliente", _try_capture_telefono(mensaje, state)
        # dirección
        if not state.get("direccion"):
            return state, "Caliente", _try_capture_direccion(mensaje, state)
        # ciudad (y resumen)
        if not state.get("ciudad"):
            return state, "Caliente", _try_capture_ciudad(mensaje, state)

        # confirmación
        if any(x in mensaje for x in ["sí", "si", "correcto", "dale", "confirmo", "ok", "listo"]):
            falt = _missing_fields(state)
            if falt:
                return state, "Caliente", _ask_for_next_missing(state)
            return state, "Cierre", "🎉 ¡Pedido confirmado! En breve te enviaremos los detalles del envío."

        # si no confirma, re-mostramos el resumen/pendiente
        return state, "Caliente", _ask_for_next_missing(state)

    # 4) Fallback
    state["fase"] = "frio"
    return state, "Frio", "¡Hola! 👋 ¿Quieres ver los modelos o saber los precios? Escribe “precio” o dime un modelo (ej. “titanium”)."