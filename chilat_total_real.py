import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36",
     "Content-Type": "application/json", "Accept": "application/json",
     "Origin": "https://shop.chilat.com", "Referer": "https://shop.chilat.com/goods/list/all"}
URL = "https://shop.chilat.com/api/pages/GoodsListPage/getPageData"
body = {"categoryId": "0", "keyword": "", "minPrice": None, "maxPrice": None,
        "pageNo": 1, "pageSize": 20, "imageId": "", "childCategoryId": "",
        "marketingRuleId": "", "padc": ""}
r = requests.post(URL, headers=H, data=json.dumps(body), timeout=30)
d = r.json()
data = d["data"]
print("status:", r.status_code, "| code:", d["result"]["code"])
print("keys data:", list(data.keys()))

# total de la pagina / paginacion
for k in data:
    if any(t in k.lower() for t in ["total", "count", "page", "size"]):
        print("  ", k, "=", data[k])

tree = data["categoryTree"]

def walk(node, depth=0, top=None):
    rows = []
    name = node.get("cateName")
    gc = node.get("goodsCount")
    if depth == 1:
        top = name
    if depth >= 1:
        rows.append((depth, top, name, gc))
    for ch in (node.get("children") or []):
        rows.extend(walk(ch, depth+1, top))
    return rows

rows = walk(tree)
# Totales por categoria madre = goodsCount del nodo de profundidad 1
print("\n=== goodsCount por CATEGORIA MADRE ===")
tot = 0
madres = [r for r in rows if r[0] == 1]
for depth, top, name, gc in madres:
    print(f"  {name:32} {gc:>10,}" if gc is not None else f"  {name:32} (sin count)")
    if gc: tot += gc
print(f"\n  >>> SUMA categorias madre: {tot:,}")

# hojas con count para sanity
hojas = [r for r in rows if r[3]]
print(f"\n  nodos con goodsCount: {len(hojas)} | subcategoria mas grande:",
      max(hojas, key=lambda x: x[3])[2], f"({max(h[3] for h in hojas):,})")
