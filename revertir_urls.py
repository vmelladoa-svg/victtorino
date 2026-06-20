"""Revierte el cambio /product-category/ → /categoria-producto/ en todos los productos y categorías.
La URL canónica del sitio es /categoria-producto/."""
import sys, io, time, re, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

PATRON = re.compile(r"/product-category/")


def safe_put(path, body):
    for n in range(1, 4):
        try:
            r = requests.put(f"{WC}/wp-json/wc/v3/{path}", json=body, params=P, timeout=120)
            if r.status_code == 503:
                time.sleep(8 * n); continue
            if r.status_code >= 400:
                return None
            return r.json()
        except Exception:
            time.sleep(4 * n)
    return None


print("[1/2] Buscando productos con /product-category/...")
productos_fix = []
page = 1
while True:
    r = requests.get(f"{WC}/wp-json/wc/v3/products",
                     params={**P, "per_page": 100, "page": page, "status": "any"}, timeout=60)
    if r.status_code != 200: break
    d = r.json()
    if not d: break
    for p in d:
        desc = p.get("description", "") or ""
        short = p.get("short_description", "") or ""
        if PATRON.search(desc) or PATRON.search(short):
            productos_fix.append({"id": p["id"], "name": p["name"][:50],
                                  "desc": desc, "short": short})
    if int(r.headers.get("X-WP-TotalPages", 1)) <= page: break
    page += 1
print(f"      {len(productos_fix)} productos a revertir")

for p in productos_fix:
    body = {
        "description": PATRON.sub("/categoria-producto/", p["desc"]),
        "short_description": PATRON.sub("/categoria-producto/", p["short"]),
    }
    res = safe_put(f"products/{p['id']}", body)
    print(f"  {p['id']:5}  {'OK' if res else 'FALLO'}  {p['name']}")
    time.sleep(0.6)

print("\n[2/2] Categorías...")
r = requests.get(f"{WC}/wp-json/wc/v3/products/categories",
                 params={**P, "per_page": 100}, timeout=30)
cats_fix = []
for c in r.json():
    desc = c.get("description", "") or ""
    if PATRON.search(desc):
        cats_fix.append({"id": c["id"], "name": c["name"], "desc": desc})
print(f"      {len(cats_fix)} categorías a revertir")

for c in cats_fix:
    body = {"description": PATRON.sub("/categoria-producto/", c["desc"])}
    res = safe_put(f"products/categories/{c['id']}", body)
    print(f"  cat {c['id']:3}  {'OK' if res else 'FALLO'}  {c['name']}")
    time.sleep(0.6)

print(f"\nTotal revertido: {len(productos_fix)} productos + {len(cats_fix)} categorías")
