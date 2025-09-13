# bot/loader.py
import pandas as pd
from pathlib import Path

# BASE = raíz del proyecto (carpeta que contiene /data y /bot)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "products.csv"

def load_products() -> pd.DataFrame:
    """
    Asumimos CSV correcto con encabezados:
    Id,Nombre,Descripción,Precio,Color,Talla,image_url
    y precios SIN separador de miles (e.g. 159900).
    """
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", dtype=str)

    # Aceptar "Descripcion" sin tilde también
    if "Descripción" not in df.columns and "Descripcion" in df.columns:
        df = df.rename(columns={"Descripcion": "Descripción"})

    # Asegurar columnas
    needed = ["Id", "Nombre", "Descripción", "Precio", "Color", "Talla", "image_url"]
    for c in needed:
        if c not in df.columns:
            df[c] = ""

    # Limpiar precio -> entero
    df["Precio"] = (
        df["Precio"]
        .astype(str)
        .str.replace(r"[^\d]", "", regex=True)  # por si quedó algún punto/coma
        .replace("", "0")
        .astype(int)
    )

    # Trim strings
    for c in ["Id", "Nombre", "Descripción", "Color", "Talla", "image_url"]:
        df[c] = df[c].astype(str).str.strip()

    # Filtrar filas sin nombre
    df = df[df["Nombre"] != ""].copy()
    return df

def _dedupe_by_nombre(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deja una fila por 'Nombre' (precio menor si hay variaciones por talla/color).
    """
    if df.empty:
        return df
    return (
        df.sort_values(["Nombre", "Precio"])
          .groupby("Nombre", as_index=False)
          .agg({"Descripción": "first", "Precio": "first"})
    )

def list_products() -> str:
    """
    Catálogo resumido para chat (nombre + desc + precio formateado).
    """
    df = load_products()
    if df.empty:
        return "⚠️ No hay productos cargados."
    agg = _dedupe_by_nombre(df)
    lines = []
    for _, row in agg.iterrows():
        desc = f" ({row['Descripción']})" if row["Descripción"] else ""
        precio_fmt = f"${row['Precio']:,}".replace(",", ".")
        lines.append(f"- {row['Nombre']}{desc} 👉 {precio_fmt}")
    return "\n".join(lines)

def find_product_by_name(query: str):
    """
    Coincidencia parcial en Nombre o Descripción. Devuelve dict o lista.
    """
    df = load_products()
    q = (query or "").strip().lower()
    if not q or df.empty:
        return None
    mask = (
        df["Nombre"].str.lower().str.contains(q, na=False) |
        df["Descripción"].str.lower().str.contains(q, na=False)
    )
    subset = df[mask]
    if subset.empty:
        return None
    dedup = _dedupe_by_nombre(subset)
    if len(dedup) == 1:
        return dedup.iloc[0].to_dict()
    return dedup.to_dict(orient="records")

# ======== NUEVO: helpers para el mensaje de PRECIO ========
def get_unique_models(limit: int = 2):
    """
    Devuelve hasta 'limit' modelos únicos (Nombre, Descripción, Precio) para armar frases.
    """
    df = load_products()
    if df.empty:
        return []
    agg = _dedupe_by_nombre(df)
    # Nos quedamos con las primeras 'limit' filas
    models = []
    for _, row in agg.head(limit).iterrows():
        models.append({
            "Nombre": row["Nombre"],
            "Descripción": row["Descripción"],
            "Precio": int(row["Precio"]),
        })
    return models

def build_price_message():
    """
    Construye:
    "Perfecto, tenemos estos modelos de calzado disponibles:
     zapato A ... en oferta $X y el zapato B ... en oferta $Y.
     ¿Cuál de los dos desea?"
    """
    models = get_unique_models(2)
    if not models:
        return "⚠️ No hay productos cargados."
    if len(models) == 1:
        m1 = models[0]
        p1 = f"${m1['Precio']:,}".replace(",", ".")
        return (f"Perfecto, tenemos disponible: {m1['Nombre']} que está hoy en oferta y le queda en {p1}. "
                f"¿Desea este modelo?")
    # dos modelos
    m1, m2 = models[0], models[1]
    p1 = f"${m1['Precio']:,}".replace(",", ".")
    p2 = f"${m2['Precio']:,}".replace(",", ".")
    return (f"Perfecto, tenemos estos modelos de calzado disponibles: "
            f"{m1['Nombre']} que está hoy en oferta y le queda en {p1} "
            f"y {m2['Nombre']} que también está en oferta y le queda en {p2}. "
            f"¿Cuál de los dos desea?")