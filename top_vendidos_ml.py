"""
Lista los top vendidos historicos de ML C3 segun el campo sold_quantity del item.
Cruza con WooCommerce para detectar cuales ya estan en la web.
"""
import json
import sys
import io
import requests
import re
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json", encoding="utf-8") as f:
    tk = json.load(f)
ML_HEAD = {"Authorization": f"Bearer {tk['access_token']}"}
USER_ID = tk["user_id"]


def normalizar(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    ruido = {"envio", "gratis", "nuevo", "oferta", "promo", "stock", "ml", "mlc",
             "victtorino", "victorino", "chile", "para", "con", "sin", "de", "del",
             "la", "el", "los", "las", "un", "una", "y", "o", "en", "cm", "mm", "x"}
    return " ".join(sorted(t for t in s.split() if t and t not in ruido and len(t) > 1))


print("[1/3] Listando todos los activos de ML C3...")
all_ids = []
scroll = None
while True:
    params = {"status": "active", "limit": 100, "search_type": "scan"}
    if scroll:
        params["scroll_id"] = scroll
    r = requests.get(f"https://api.mercadolibre.com/users/{USER_ID}/items/search",
                     headers=ML_HEAD, params=params, timeout=30)
    d = r.json()
    all_ids.extend(d.get("results", []))
    scroll = d.get("scroll_id")
    if not scroll or not d.get("results"):
        break
print(f"      total activos: {len(all_ids)}")

print("[2/3] Trayendo sold_quantity multiget (batches de 20)...")
items = []
for i in range(0, len(all_ids), 20):
    batch = ",".join(all_ids[i:i + 20])
    r = requests.get("https://api.mercadolibre.com/items", headers=ML_HEAD,
                     params={"ids": batch, "attributes": "id,title,sold_quantity,price,available_quantity,permalink,thumbnail"},
                     timeout=30)
    for entry in r.json():
        if entry.get("code") == 200:
            items.append(entry["body"])

# Ordenar por sold_quantity
items.sort(key=lambda x: x.get("sold_quantity", 0) or 0, reverse=True)
top = [i for i in items if (i.get("sold_quantity") or 0) > 0][:20]
print(f"      con ventas: {sum(1 for i in items if (i.get('sold_quantity') or 0) > 0)} (mostrare top 20)")

print("\n[3/3] Cruzando con Woo para ver cuales ya estan en la web...")
# Cargar productos Woo
woo_prods = []
page = 1
while True:
    r = requests.get(f"{WC}/wp-json/wc/v3/products",
                     params={**P, "per_page": 100, "page": page, "status": "any"},
                     timeout=30)
    if r.status_code != 200:
        break
    d = r.json()
    if not d:
        break
    woo_prods.extend(d)
    if int(r.headers.get("X-WP-TotalPages", 1)) <= page:
        break
    page += 1
print(f"      productos Woo: {len(woo_prods)}")

# Para cada top, buscar por SKU ML-{id} o por similitud
import difflib

def buscar_en_woo(ml_id, ml_titulo):
    # primero SKU
    for w in woo_prods:
        if w.get("sku") == f"ML-{ml_id}":
            return w
    # luego similitud
    n_ml = normalizar(ml_titulo)
    mejor, score = None, 0.0
    for w in woo_prods:
        n_w = normalizar(w.get("name", ""))
        if not n_w:
            continue
        s = difflib.SequenceMatcher(None, n_ml, n_w).ratio()
        toks_ml = set(n_ml.split())
        toks_w = set(n_w.split())
        if toks_ml and toks_w:
            jac = len(toks_ml & toks_w) / len(toks_ml | toks_w)
            s = max(s, jac)
        if s > score:
            score = s
            mejor = w
    return mejor if score >= 0.7 else None

print("\n" + "=" * 80)
print(f"TOP 20 VENDIDOS HISTORICOS EN ML C3")
print("=" * 80)
salida = []
for i, item in enumerate(top, start=1):
    woo = buscar_en_woo(item["id"], item["title"])
    woo_info = ""
    if woo:
        woo_info = f"-> Woo {woo['id']} [{woo.get('status')}] {[c['name'] for c in woo.get('categories',[])]}"
    else:
        woo_info = "-> NO EN WEB"
    print(f"{i:2}. {item.get('sold_quantity'):4} ventas | ${item.get('price'):>7} | stock={item.get('available_quantity'):3} | {item['title'][:50]}")
    print(f"     ML: {item['id']}  {woo_info}")
    salida.append({
        "ranking": i,
        "ml_id": item["id"],
        "titulo": item["title"],
        "ventas": item.get("sold_quantity"),
        "precio": item.get("price"),
        "stock": item.get("available_quantity"),
        "permalink": item.get("permalink"),
        "woo_id": woo["id"] if woo else None,
        "woo_name": woo["name"] if woo else None,
        "woo_status": woo["status"] if woo else None,
        "woo_categorias": [c["name"] for c in (woo.get("categories", []) if woo else [])],
    })

with open(r"C:\Users\dell\victtorino\top_vendidos_ml.json", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
print(f"\nDetalle -> top_vendidos_ml.json")
