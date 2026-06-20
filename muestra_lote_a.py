"""Muestra 5 productos del Lote A (sin focus, descripción ≥200 palabras) con el focus propuesto."""
import json, sys, io, re, requests, random, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

with open(r"C:\Users\dell\victtorino\analisis_seo_huerfanos.json", encoding="utf-8") as f:
    data = json.load(f)
ids_lote_a = data["sin_focus_desc_decente"]
print(f"Total Lote A: {len(ids_lote_a)}\n")


def normalizar(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return s.lower().strip()


def proponer_focus(titulo, categoria):
    """Genera focus keyword basado en título + categoría."""
    t = normalizar(titulo)

    # Extraer medida común (80x44, 100x44, 25 cm, 90mm, 1 1/2, etc.)
    medida_match = re.search(r"(\d{2,3}\s*x\s*\d{2,3}|\d+\s*1?/\d|\d+\s*(?:ml|cm|mm|lts?|l|metros))", t)
    medida = medida_match.group(1).replace(" ", "") if medida_match else ""

    # Modelo
    modelos = ["colomba", "domenica", "notte", "modern", "taumm", "schwartz",
               "hannover", "leonardo", "neue", "freiburg", "schwarz", "dusseldorf",
               "victtorino"]
    modelo = next((m for m in modelos if m in t), "")

    # Color
    colores = ["negro", "blanco", "plateado", "cromado", "cepillado", "inox",
               "bronce", "transparente", "rosa", "verde", "azul", "dorado"]
    color = next((c for c in colores if c in t), "")

    # Generar focus por tipo de producto
    if "llave monomando lavamanos" in t or "llave monomando lavatorio" in t or "monomando lavamanos" in t:
        return f"llave monomando lavamanos {modelo or color}".strip()
    if "llave monomando lavaplatos" in t or "monomando lavaplatos" in t:
        return f"llave monomando lavaplatos {modelo or color}".strip()
    if "monomando ducha" in t or "monomando tina" in t:
        return f"monomando ducha {modelo or color}".strip()
    if "llave monomando" in t:
        return f"llave monomando {modelo or color}".strip()
    if "lavaplatos sobrepuesto" in t or "lavaplatos sobreponer" in t:
        return f"lavaplatos sobrepuesto {medida}".strip()
    if "lavaplatos empotrado" in t or "lavaplatos empotrable" in t:
        return f"lavaplatos empotrado {medida}".strip()
    if "lavaplatos" in t:
        return f"lavaplatos {medida}".strip()
    if "lavamanos" in t and "vidrio" in t:
        return f"lavamanos vidrio {medida}".strip()
    if "lavamanos" in t and ("sobrepuesto" in t or "sobreponer" in t):
        return f"lavamanos sobrepuesto {medida}".strip()
    if "lavamanos" in t:
        return f"lavamanos {modelo or color or medida}".strip()
    if "shower door" in t:
        return f"shower door {medida}".strip()
    if "receptor" in t and "ducha" in t:
        return f"receptor ducha {medida}".strip()
    if "plato" in t and "ducha" in t:
        return f"plato ducha {medida or color}".strip()
    if "espejo" in t:
        if "led" in t:
            return f"espejo led baño {medida}".strip()
        return f"espejo baño {medida or modelo}".strip()
    if "tina" in t:
        return f"tina baño {medida or modelo}".strip()
    if "wc" in t or "estanque" in t or "valvula" in t:
        return f"wc {modelo or medida}".strip() or "kit wc"
    if "sifón" in t or "sifon" in t:
        return f"sifón {medida or color}".strip()
    if "dispensador" in t:
        return f"dispensador {modelo or color or medida}".strip()
    if "agarradera" in t or "barra de seguridad" in t or "barra seguridad" in t:
        return f"agarradera baño {medida or modelo}".strip()
    if "basurero" in t or "papelero" in t:
        return f"basurero pedal {medida}".strip()
    if "set" in t and ("baño" in t or "accesorios" in t):
        return f"set accesorios baño {modelo}".strip()
    if "flexible" in t and "agua" in t:
        return f"flexible agua {medida}".strip()
    if "ducha" in t:
        return f"ducha {modelo or color or medida}".strip()
    # Fallback
    return categoria.lower() if categoria else "producto baño"


# Tomar 5 muestras variadas
random.seed(7)
sample_ids = random.sample(ids_lote_a, min(5, len(ids_lote_a)))

print(f"{'ID':5} {'CAT':18} {'TITULO':50} → FOCUS PROPUESTO\n" + "-" * 120)
for pid in sample_ids:
    r = requests.get(f"{WC}/wp-json/wc/v3/products/{pid}", params=P, timeout=30).json()
    titulo = r.get("name", "")
    cat = (r.get("categories") or [{"name": ""}])[0]["name"]
    focus = proponer_focus(titulo, cat)
    plain = re.sub(r"<[^>]+>", " ", r.get("description", ""))
    pal = len(plain.split())
    print(f"{pid:5} {cat[:18]:18} {titulo[:50]:50} → \"{focus}\" ({pal} pal)")
