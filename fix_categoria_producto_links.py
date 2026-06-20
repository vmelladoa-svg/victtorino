"""
Reemplaza todos los enlaces internos /categoria-producto/{slug}/ por /product-category/{slug}/
en descripciones de productos y categorías.

Los enlaces /categoria-producto/ son interpretados por WP como productos en algunos casos
(routing ambiguo). La URL canónica correcta es /product-category/{slug}/.
"""
import sys, io, time, re, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

PATRON = re.compile(r"/categoria-producto/", re.IGNORECASE)

def safe_put(path, body):
    for n in range(1, 4):
        try:
            r = requests.put(f"{WC}/wp-json/wc/v3/{path}", json=body, params=P, timeout=120)
            if r.status_code == 503:
                time.sleep(8 * n); continue
            if r.status_code >= 400:
                print(f"    HTTP {r.status_code}")
                return None
            return r.json()
        except Exception as e:
            print(f"    err {type(e).__name__}; retry")
            time.sleep(4 * n)
    return None


# 1) Productos
print("[1/2] Buscando y arreglando productos...")
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
print(f"      {len(productos_fix)} productos con enlaces a /categoria-producto/")

for pid_info in productos_fix:
    new_desc = PATRON.sub("/product-category/", pid_info["desc"])
    new_short = PATRON.sub("/product-category/", pid_info["short"])
    body = {"description": new_desc, "short_description": new_short}
    res = safe_put(f"products/{pid_info['id']}", body)
    if res:
        print(f"  {pid_info['id']:5}  fixed  {pid_info['name']}")
    else:
        print(f"  {pid_info['id']:5}  FALLO  {pid_info['name']}")
    time.sleep(0.5)

# 2) Categorías
print("\n[2/2] Buscando y arreglando categorías...")
r = requests.get(f"{WC}/wp-json/wc/v3/products/categories",
                 params={**P, "per_page": 100}, timeout=30)
cats_fix = []
for c in r.json():
    desc = c.get("description", "") or ""
    if PATRON.search(desc):
        cats_fix.append({"id": c["id"], "name": c["name"], "desc": desc})
print(f"      {len(cats_fix)} categorías con enlaces a /categoria-producto/")

for c in cats_fix:
    new_desc = PATRON.sub("/product-category/", c["desc"])
    res = safe_put(f"products/categories/{c['id']}", {"description": new_desc})
    if res:
        print(f"  cat {c['id']:3}  fixed  {c['name']}")
    else:
        print(f"  cat {c['id']:3}  FALLO  {c['name']}")
    time.sleep(0.5)

print(f"\nTotal arreglado: {len(productos_fix)} productos + {len(cats_fix)} categorías")
