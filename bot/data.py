# bot/data.py

# ========================
# RESPUESTAS CALIENTES
# ========================
respuestas_caliente = {
    ("adquirir",): "¡Excelente elección! 🙌 Para adquirirlo dime tu talla primero.",
    ("comprar", "quiero comprar", "lo compro", "deseo comprar"): "¡Perfecto! 🚀 Solo necesito confirmar tu talla. ¿Cuál es tu talla?",
    ("quiero", "quisiera", "me interesa"): "¡Perfecto! 😍 Dime tu talla y seguimos.",
    ("reservar", "resérvalo", "quiero reservar"): "¡Genial! ✅ Dime tu talla para reservarlo ya mismo.",
    ("pedido", "hacer pedido", "mi pedido"): "¡De una! 🚀 Dime tu talla para gestionar tu pedido.",
    ("pago", "quiero pagar", "listo para pagar"): "Aceptamos transferencia, tarjeta y contraentrega 💳. ¿Cuál prefieres?",
    ("envío", "enviar", "despacho", "mandalo", "mándalo"): "Hacemos envíos a todo el país 📦. Dime tu ciudad y te confirmo costo y tiempo de entrega.",
    ("correcto", "si es correcto", "dale", "envíelo", "envialo", "sí envíelo", "sí, correcto"): "Perfecto 🚀, procedemos a despachar tu pedido 🙌"
}

# ========================
# RESPUESTAS TIBIAS
# ========================
respuestas_tibio = {
    "color": "Tenemos varios colores disponibles: Azul, negro y marrón 🎨. ¿Quieres que te muestre fotos?",
    "colores": "¡Claro! Contamos con varias opciones. ¿Cuál prefieres ver primero?",
    "azul": "Perfecto, tomamos nota del color azul 🎨. Ahora dime tu talla para continuar.",
    "negro": "Perfecto, tomamos nota del color negro 🎨. Ahora dime tu talla para continuar.",
    "marrón": "Perfecto, tomamos nota del color marrón 🎨. Ahora dime tu talla para continuar.",
    "cuánto cuesta": "El precio está en promoción especial 💰. ¿Quieres que te lo confirme con envío?",
    "costo": "El valor depende del modelo y la ciudad 💵. ¿Me compartes tu ciudad?",
    "modelo": "Tenemos varios modelos 🔥. ¿Quieres que te muestre el catálogo?",
    "sintetico": "Excelente decisión, viene en colores azul, negro y marrón y su precio es de $149.900, ¿cuál color le gustaría?"
}

# ========================
# RESPUESTAS FRÍAS
# ========================
respuestas_frio = {
    ("hola", "buenas", "buenos días", "buenas tardes"): "¡Hola! 👋 Bienvenido 🙌. ¿Quieres ver los modelos más vendidos?",
    ("gracias", "muchas gracias"): "¡Gracias a ti! 🙏 ¿Quieres que te envíe fotos?",
    ("catálogo", "catalogo", "quiero ver catálogo", "muestrame catálogo"): "¡Claro! 📖 Tenemos zapatos en cuero genuino y sintético 👉 [link]. ¿Cuál prefieres?",
    ("precio", "valor", "cuánto valen"): "Con mucho gusto 💵. Tenemos zapatos en cuero genuino y sintético. ¿Cuál prefieres?",
    "si": "Tenemos disponibles: Zapato casual clásico, elaborado en cuero genuino y Zapato titaniun deportivo, elaborados en cuero sintético, ¿Cual prefiere?🎨."
}