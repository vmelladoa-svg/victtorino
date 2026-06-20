"""Extrae los productos de una categoria WooCommerce y genera JSON para la maqueta.

Uso: python extraer_categoria_maqueta.py <id_categoria> <nombre_slug_pagina>
Ejemplo: python extraer_categoria_maqueta.py 116 espejos
"""
import json
import re
import sys
import requests
from html import unescape
from pathlib import Path

WC_URL = "https://victtorino.cl"
WC_KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
WC_SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

OUT_DIR = Path("data/maqueta/productos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

def html_a_texto(html):
    if not html:
        return ""
    txt = unescape(TAG_RE.sub(" ", html))
    return WS_RE.sub(" ", txt).strip()

def bajar_productos(cat_id):
    out = []
    page = 1
    while True:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            params={
                "per_page": 100,
                "page": page,
                "category": cat_id,
                "status": "publish",
                "orderby": "menu_order",
                "order": "asc",
            },
            auth=(WC_KEY, WC_SEC),
            timeout=120,
        )
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:300]}")
            break
        data = r.json()
        if not data:
            break
        out.extend(data)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return out

def limpiar(p):
    return {
        "id": p["id"],
        "name": p["name"],
        "slug": p["slug"],
        "sku": p.get("sku") or None,
        "permalink": p.get("permalink"),
        "price": p.get("price") or None,
        "regular_price": p.get("regular_price") or None,
        "sale_price": p.get("sale_price") or None,
        "on_sale": p.get("on_sale", False),
        "stock_status": p.get("stock_status"),
        "stock_quantity": p.get("stock_quantity"),
        "short_description": html_a_texto(p.get("short_description")),
        "description": html_a_texto(p.get("description")),
        "categorias": [{"id": c["id"], "name": c["name"], "slug": c["slug"]} for c in (p.get("categories") or [])],
        "atributos": [
            {
                "name": a.get("name"),
                "options": a.get("options") or [],
            }
            for a in (p.get("attributes") or [])
        ],
        "imagenes": [
            {"src": i.get("src"), "alt": i.get("alt") or i.get("name"), "id": i.get("id")}
            for i in (p.get("images") or [])
        ],
        "featured": p.get("featured", False),
        "average_rating": p.get("average_rating") or "0",
        "rating_count": p.get("rating_count") or 0,
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python extraer_categoria_maqueta.py <id_categoria> <nombre_slug_pagina>")
        sys.exit(1)
    cat_id = int(sys.argv[1])
    slug = sys.argv[2]

    print(f"Bajando productos de categoria {cat_id}...")
    raw = bajar_productos(cat_id)
    print(f"  {len(raw)} productos brutos")
    productos = [limpiar(p) for p in raw]

    out_file = OUT_DIR / f"{slug}.json"
    payload = {
        "categoria_pagina": slug,
        "categoria_wc_id": cat_id,
        "total_productos": len(productos),
        "productos": productos,
    }
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK guardado en {out_file}")
    print(f"  Tamano: {out_file.stat().st_size / 1024:.1f} KB")
    print(f"  Productos: {len(productos)}")
    print()
    print("=== MUESTRA (primer producto) ===")
    if productos:
        p = productos[0]
        print(f"  Nombre:    {p['name']}")
        print(f"  SKU:       {p['sku']}")
        print(f"  Precio:    {p['price']}")
        print(f"  Stock:     {p['stock_status']}")
        print(f"  Imagenes:  {len(p['imagenes'])}")
        print(f"  Atributos: {len(p['atributos'])}")
