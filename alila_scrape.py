"""
Scrape alila.top (WooCommerce Store API pública) -> todos los productos con precio y fotos.
Salida: alila_productos.xlsx + carpeta alila_fotos/ (foto principal de cada uno).
Solo lee datos públicos.
"""
import requests, sys, io, re
from pathlib import Path
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
ROOT = Path(r"C:\Users\dell\victtorino")
IMGDIR = ROOT / "alila_fotos"
IMGDIR.mkdir(exist_ok=True)
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
B = "https://alila.top/wp-json/wc/store/v1/products"


def precio(p):
    pr = p.get("prices", {})
    mu = int(pr.get("currency_minor_unit", 0) or 0)
    def conv(v):
        if v in (None, ""):
            return None
        try:
            return round(int(v) / (10 ** mu), 2) if mu else int(v)
        except Exception:
            return v
    return conv(pr.get("price")), conv(pr.get("regular_price")), conv(pr.get("sale_price")), pr.get("currency_code")


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


rows, page = [], 1
while True:
    r = requests.get(B, headers=H, params={"per_page": 100, "page": page}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not data:
        break
    for p in data:
        pv, reg, sale, cur = precio(p)
        imgs = [im.get("src") for im in (p.get("images") or []) if im.get("src")]
        cats = ", ".join(c.get("name", "") for c in (p.get("categories") or []))
        main = imgs[0] if imgs else ""
        local = ""
        if main:
            try:
                rr = requests.get(main.split("?")[0], headers=H, timeout=25)
                if rr.status_code == 200 and len(rr.content) > 500:
                    safe = re.sub(r"[^A-Za-z0-9_\-]", "_", (p.get("sku") or p.get("slug") or str(p["id"])))[:40]
                    fp = IMGDIR / f"{safe}.jpg"
                    fp.write_bytes(rr.content)
                    local = fp.name
            except Exception:
                pass
        rows.append({
            "Nombre": p.get("name"),
            "SKU": p.get("sku"),
            "Categoría": cats,
            "Precio CLP": pv,
            "Precio normal": reg,
            "Precio oferta": sale,
            "Moneda": cur,
            "En stock": p.get("is_in_stock"),
            "N° fotos": len(imgs),
            "URL producto": p.get("permalink"),
            "Descripción": strip_html(p.get("short_description") or p.get("description"))[:500],
            "Foto principal": main,
            "Foto local": local,
            "Todas las fotos": " | ".join(imgs),
            "id": p.get("id"),
        })
        print(f"  {p.get('id'):>4} {str(pv):>8} {cur}  {len(imgs)}f  {str(p.get('name'))[:45]}")
    page += 1

df = pd.DataFrame(rows)
out = ROOT / "alila_productos.xlsx"
df.to_excel(out, index=False)
print(f"\n=== LISTO: {len(df)} productos ===")
print(f"Excel: {out}")
print(f"Fotos: {IMGDIR} ({len(list(IMGDIR.glob('*.jpg')))} jpg)")
