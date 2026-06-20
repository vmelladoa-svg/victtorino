"""
Cruza catalogo activo ML C3 contra WooCommerce para identificar la DIFERENCIA.

Tres categorias de output:
- YA_EN_WEB: match alto -> no transferir
- DUDOSOS  : match medio (60-85%) -> revision manual
- FALTANTES: sin match >60% -> candidatos a importar
"""
import json
import sys
import io
import re
import unicodedata
import requests
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"


def normalizar(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # quita tildes
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    # quita ruido comercial frecuente
    ruido = {"envio", "gratis", "nuevo", "oferta", "promo", "stock", "kit", "set",
             "ml", "mlc", "victtorino", "victorino", "chile", "para", "con", "sin",
             "de", "del", "la", "el", "los", "las", "un", "una", "y", "o", "en",
             "cm", "mm", "x"}
    tokens = [t for t in s.split() if t and t not in ruido and len(t) > 1]
    return " ".join(sorted(tokens))


def listar_woo_productos():
    """Trae todos los productos publicados de Woo (cualquier status excepto trash)."""
    out = []
    page = 1
    while True:
        r = requests.get(
            f"{WC}/wp-json/wc/v3/products",
            params={"consumer_key": KEY, "consumer_secret": SEC,
                    "per_page": 100, "page": page,
                    "status": "any"},  # publish + draft + private
            timeout=30,
        )
        if r.status_code >= 400:
            print(f"ERROR Woo {r.status_code}: {r.text[:200]}")
            break
        d = r.json()
        if not d:
            break
        out.extend(d)
        if int(r.headers.get("X-WP-TotalPages", 1)) <= page:
            break
        page += 1
    return out


# 1) Cargar ML
print("[1/4] Cargando items ML C3 desde analisis_categorias_c3.json...")
with open(r"C:\Users\dell\victtorino\analisis_categorias_c3.json", encoding="utf-8") as f:
    ml_data = json.load(f)
ml_items = ml_data["items"]
print(f"      {len(ml_items)} items activos ML")

# 2) Cargar Woo
print("[2/4] Trayendo catalogo Woo en vivo (todos los status)...")
woo_items = listar_woo_productos()
print(f"      {len(woo_items)} productos en Woo")

# 3) Normalizar
print("[3/4] Normalizando titulos y cruzando...")
woo_norm = [(w["id"], w["name"], normalizar(w["name"]), w.get("sku", ""), w.get("status"))
            for w in woo_items]

ya_en_web = []
dudosos = []
faltantes = []

for ml in ml_items:
    ml_id = ml["ml_id"]
    titulo_ml = ml["titulo"]
    n_ml = normalizar(titulo_ml)
    if not n_ml:
        continue
    mejor_score = 0.0
    mejor = None
    for wid, wname, n_w, sku, status in woo_norm:
        if not n_w:
            continue
        score = SequenceMatcher(None, n_ml, n_w).ratio()
        # bonus si los tokens calzan mucho (ignora orden)
        toks_ml = set(n_ml.split())
        toks_w = set(n_w.split())
        if toks_ml and toks_w:
            jaccard = len(toks_ml & toks_w) / len(toks_ml | toks_w)
            score = max(score, jaccard)
        if score > mejor_score:
            mejor_score = score
            mejor = (wid, wname, sku, status)

    registro = {
        "ml_id": ml_id,
        "ml_titulo": titulo_ml,
        "ml_stock": ml["stock"],
        "ml_cat": ml["cat_leaf"],
        "score": round(mejor_score, 2),
        "woo_match": mejor,
    }
    if mejor_score >= 0.85:
        ya_en_web.append(registro)
    elif mejor_score >= 0.60:
        dudosos.append(registro)
    else:
        faltantes.append(registro)

# 4) Reporte
print(f"[4/4] Resultado:")
print(f"      YA_EN_WEB (score>=0.85): {len(ya_en_web)}")
print(f"      DUDOSOS   (0.60-0.85)  : {len(dudosos)}")
print(f"      FALTANTES (<0.60)      : {len(faltantes)}")

# Guardar JSON detallado
out_path = r"C:\Users\dell\victtorino\cruce_ml_woo_resultado.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"ya_en_web": ya_en_web, "dudosos": dudosos, "faltantes": faltantes},
              f, ensure_ascii=False, indent=2)
print(f"      detalle -> {out_path}")

# Distribucion de faltantes por categoria ML
from collections import Counter
print("\n" + "=" * 70)
print("FALTANTES por categoria ML (top)")
print("=" * 70)
cat_falt = Counter(r["ml_cat"] for r in faltantes)
for c, n in cat_falt.most_common(15):
    print(f"  {n:>3}  {c}")

print("\n" + "=" * 70)
print("Muestra de FALTANTES (10 primeros)")
print("=" * 70)
for r in faltantes[:10]:
    print(f"  [{r['ml_cat'][:25]:25}] {r['ml_titulo'][:60]} (stock={r['ml_stock']}, score={r['score']})")

print("\n" + "=" * 70)
print("Muestra de DUDOSOS (10 primeros)")
print("=" * 70)
for r in dudosos[:10]:
    woo = r["woo_match"]
    print(f"  ML: {r['ml_titulo'][:50]}")
    print(f"  WOO: {woo[1][:50] if woo else '-'} (score={r['score']})")
    print()
