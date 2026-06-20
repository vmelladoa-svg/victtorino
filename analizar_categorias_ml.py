"""
Analiza categorias del catalogo activo de ML C3.
- Lista todos los items activos
- Trae category_id de cada uno (multiget batch 20)
- Resuelve nombre legible de cada categoria ML (/categories/{id})
- Agrupa por categoria y cuenta
- Cruza con categorias Woo existentes
- Reporta: categorias ML con N>=5 productos que NO existen en Woo (propuestas)
"""
import json
import sys
import io
import requests
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json", encoding="utf-8") as f:
    tk = json.load(f)
ML_TOKEN = tk["access_token"]
USER_ID = tk["user_id"]
HEAD = {"Authorization": f"Bearer {ML_TOKEN}"}

WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"


def listar_todos_los_ids():
    ids = []
    scroll = None
    while True:
        params = {"status": "active", "limit": 100, "search_type": "scan"}
        if scroll:
            params["scroll_id"] = scroll
        r = requests.get(
            f"https://api.mercadolibre.com/users/{USER_ID}/items/search",
            headers=HEAD, params=params, timeout=30,
        )
        r.raise_for_status()
        d = r.json()
        ids.extend(d.get("results", []))
        scroll = d.get("scroll_id")
        if not scroll or not d.get("results"):
            break
    return ids


def multiget(ids):
    """Trae title, category_id, available_quantity de hasta 20 items."""
    items = []
    for i in range(0, len(ids), 20):
        batch = ",".join(ids[i:i + 20])
        r = requests.get(
            "https://api.mercadolibre.com/items",
            headers=HEAD,
            params={"ids": batch, "attributes": "id,title,category_id,available_quantity,status"},
            timeout=30,
        )
        r.raise_for_status()
        for entry in r.json():
            if entry.get("code") == 200:
                items.append(entry["body"])
    return items


def cat_path(cat_id, cache):
    if cat_id in cache:
        return cache[cat_id]
    r = requests.get(f"https://api.mercadolibre.com/categories/{cat_id}", timeout=20)
    if r.status_code != 200:
        cache[cat_id] = ([], "")
        return cache[cat_id]
    d = r.json()
    path = [n["name"] for n in d.get("path_from_root", [])]
    leaf = path[-1] if path else d.get("name", "")
    cache[cat_id] = (path, leaf)
    return cache[cat_id]


def woo_categorias():
    out = []
    page = 1
    while True:
        r = requests.get(
            f"{WC}/wp-json/wc/v3/products/categories",
            params={"consumer_key": KEY, "consumer_secret": SEC, "per_page": 100, "page": page},
            timeout=30,
        )
        d = r.json()
        if not d:
            break
        out.extend(d)
        if int(r.headers.get("X-WP-TotalPages", 1)) <= page:
            break
        page += 1
    return out


print("[1/4] Listando items activos C3...")
ids = listar_todos_los_ids()
print(f"      total activos: {len(ids)}")

print("[2/4] Trayendo category_id de cada item...")
items = multiget(ids)
print(f"      items con datos: {len(items)}")

print("[3/4] Resolviendo nombres de categorias ML...")
cache = {}
cats_por_item = []
for it in items:
    cid = it.get("category_id")
    if not cid:
        continue
    path, leaf = cat_path(cid, cache)
    cats_por_item.append({
        "ml_id": it.get("id"),
        "titulo": it.get("title", "")[:60],
        "stock": it.get("available_quantity"),
        "cat_id": cid,
        "cat_leaf": leaf,
        "cat_raiz": path[0] if path else "",
        "cat_path": " > ".join(path),
    })
print(f"      items categorizados: {len(cats_por_item)}")
print(f"      categorias ML unicas: {len(cache)}")

# Conteo
hojas = Counter(c["cat_leaf"] for c in cats_por_item)
raices = Counter(c["cat_raiz"] for c in cats_por_item)

print("\n[4/4] Cargando categorias WooCommerce existentes...")
woo_cats = woo_categorias()
woo_names = {c["name"].lower().strip() for c in woo_cats}
print(f"      Woo tiene: {sorted(c['name'] for c in woo_cats)}")

# Identificar hojas con >=5 productos
print("\n" + "=" * 70)
print("CATEGORIAS ML (hoja) con >=5 productos activos")
print("=" * 70)
print(f"{'#':>3} {'productos':>9}  {'cat ML hoja':<40} {'?en Woo':<10}")
for nombre, n in hojas.most_common():
    if n < 2:
        break
    en_woo = "SI" if nombre.lower().strip() in woo_names else "no"
    marca = ">>" if n >= 5 and en_woo == "no" else "  "
    print(f"{marca}  {n:>9}  {nombre[:40]:<40} {en_woo}")

print("\n" + "=" * 70)
print("CATEGORIAS ML (raiz) — distribucion")
print("=" * 70)
for nombre, n in raices.most_common():
    en_woo = "SI" if nombre.lower().strip() in woo_names else "no"
    print(f"  {n:>4}  {nombre[:50]:<50} {en_woo}")

# Guardar detalle por si quieres mirar
with open(r"C:\Users\dell\victtorino\analisis_categorias_c3.json", "w", encoding="utf-8") as f:
    json.dump({
        "items": cats_por_item,
        "hojas_count": dict(hojas),
        "raices_count": dict(raices),
        "woo_existentes": sorted(c["name"] for c in woo_cats),
    }, f, ensure_ascii=False, indent=2)
print("\nDetalle guardado en analisis_categorias_c3.json")
