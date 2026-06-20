"""
Scrape Chilat: grifería + lavaplatos + sanitarios (100 productos) con precio y fotos.
Salida:
  - chilat_griferia_sanitarios.xlsx  (datos + URLs de todas las fotos)
  - chilat_fotos/<sku>__0.jpg ...    (foto principal descargada de cada producto)
Solo lee datos públicos del sitio. No envía nada.
"""
import requests, json, sys, io, time, re
from pathlib import Path
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
ROOT = Path(__file__).resolve().parent
IMGDIR = ROOT / "chilat_fotos_v2"
IMGDIR.mkdir(exist_ok=True)
OUTXLSX = ROOT / "chilat_bano_cocina.xlsx"

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36",
     "Content-Type": "application/json", "Accept": "application/json",
     "Origin": "https://shop.chilat.com", "Referer": "https://shop.chilat.com/goods/list/all"}
LIST = "https://shop.chilat.com/api/pages/GoodsListPage/getPageData"
DETAIL = "https://shop.chilat.com/api/pages/GoodsDetailPage/getPageData"

# (keyword, cantidad, palabras_a_excluir_del_nombre)
PLAN = [
    ("fregadero", 25, []),
    ("inodoro", 25, ["perro", "gato", "mascota", "pet", "arena", "gatos", "perros"]),
    ("lavamanos", 25, []),
    ("ducha", 25, []),
]


def post(url, body, tries=4):
    for i in range(tries):
        try:
            r = requests.post(url, headers=H, data=json.dumps(body), timeout=30)
            if r.status_code == 200:
                return r.json()
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return None


def buscar(keyword, n, excluir=()):
    out, page = [], 1
    while len(out) < n and page <= 30:
        j = post(LIST, {"categoryId": "0", "keyword": keyword, "minPrice": None,
                        "maxPrice": None, "pageNo": page, "pageSize": 20, "imageId": "",
                        "childCategoryId": "", "marketingRuleId": "", "padc": ""})
        if not j:
            break
        lst = j["data"]["pageData"]["goodsList"]
        if not lst:
            break
        for g in lst:
            nm = (g.get("goodsName") or "").lower()
            if excluir and any(w in nm for w in excluir):
                continue
            out.append(g)
        page += 1
    return out[:n]


def galeria(gid):
    j = post(DETAIL, {"id": gid, "padc": ""})
    if not j:
        return []
    imgs = j["data"]["pageData"].get("goodsImageList") or []
    return [u if u.startswith("http") else "https:" + u for u in imgs if isinstance(u, str)]


def usd(v):
    try:
        return round(float(v), 2)
    except Exception:
        return v


rows = []
for kw, n, excl in PLAN:
    print(f"\n[{kw}] buscando {n}...")
    items = buscar(kw, n, excl)
    print(f"   obtenidos {len(items)}")
    for idx, g in enumerate(items, 1):
        gid = g["goodsId"]
        sku = g.get("goodsNo") or gid
        fotos = galeria(gid)
        main = g.get("mainImageUrl") or (fotos[0] if fotos else "")
        if main and not main.startswith("http"):
            main = "https:" + main
        # descargar foto principal
        local = ""
        if main:
            try:
                rr = requests.get(main.split("?")[0], headers=H, timeout=25)
                if rr.status_code == 200 and len(rr.content) > 800:
                    safe = re.sub(r"[^A-Za-z0-9_\-]", "_", str(sku))[:40]
                    fp = IMGDIR / f"{safe}.jpg"
                    fp.write_bytes(rr.content)
                    local = fp.name
            except Exception:
                pass
        rows.append({
            "Categoría": kw,
            "Nombre": g.get("goodsName"),
            "SKU (goodsNo)": sku,
            "Precio min USD": usd(g.get("minPrice")),
            "Precio max USD": usd(g.get("maxPrice")),
            "Unidad": g.get("goodsPriceUnitName"),
            "Compra mínima": g.get("minBuyQuantity"),
            "N° fotos": len(fotos),
            "URL producto": f"https://shop.chilat.com/goods/{gid}",
            "Foto principal": main,
            "Foto local": local,
            "Todas las fotos": " | ".join(fotos),
            "goodsId": gid,
        })
        print(f"   {idx:>3}/{len(items)}  {len(fotos)}f  ${usd(g.get('minPrice'))}  {str(g.get('goodsName'))[:45]}")
        time.sleep(0.2)

df = pd.DataFrame(rows)
out = OUTXLSX
df.to_excel(out, index=False)
print(f"\n=== LISTO: {len(df)} productos ===")
print(f"Excel: {out}")
print(f"Fotos descargadas en: {IMGDIR}  ({len(list(IMGDIR.glob('*.jpg')))} jpg)")
print("\nResumen por categoría:")
print(df.groupby("Categoría").agg(productos=("Nombre", "count"),
      precio_min=("Precio min USD", "min"), precio_max=("Precio min USD", "max")).to_string())
