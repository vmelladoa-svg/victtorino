"""Baja todo el catalogo WooCommerce y lo agrupa en las 8 paginas de la maqueta.

Reglas:
- Un producto con varias categorias WP aparece en las paginas correspondientes (en todas).
- Dedupe por id dentro de cada pagina.
- Outlet queda vacio (placeholder).
"""
import json
import re
import requests
from html import unescape
from pathlib import Path
from collections import defaultdict

WC_URL = "https://victtorino.cl"
WC_KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
WC_SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

OUT_DIR = Path("data/maqueta/productos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Mapeo: id de categoria WP -> lista de paginas maqueta a las que pertenece
WP_CAT_TO_PAGINA = {
    113: ["griferia"],                  # Griferia
    143: ["bano"],                       # Agarraderas y Barras para bano
    117: ["bano"],                       # Lavamanos
    144: ["bano"],                       # Sifones y Desagues
    115: ["cocina"],                     # Lavaplatos
    114: ["cocina"],                     # Dispensador
    118: ["shower-mamparas"],            # Shower/Mamparas/Receptaculos
    145: ["wc-inodoros"],                # WC e Inodoros
    112: ["accesorios"],                 # Accesorios
    116: ["espejos"],                    # Espejos
}

# Lista completa de paginas (incluye outlet vacio)
PAGINAS = ["griferia", "bano", "cocina", "shower-mamparas", "espejos", "wc-inodoros", "accesorios", "outlet"]

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

def html_a_texto(html):
    if not html:
        return ""
    txt = unescape(TAG_RE.sub(" ", html))
    return WS_RE.sub(" ", txt).strip()

def bajar_todos_productos():
    """Baja TODOS los productos publicados (no filtra por categoria)."""
    out = []
    page = 1
    while True:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products",
            params={
                "per_page": 100,
                "page": page,
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
        print(f"  page {page}/{total_pages} -> {len(data)} productos (acum {len(out)})")
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
        "categorias": [
            {"id": c["id"], "name": c["name"], "slug": c["slug"]}
            for c in (p.get("categories") or [])
        ],
        "atributos": [
            {"name": a.get("name"), "options": a.get("options") or []}
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

def asignar_a_paginas(producto_limpio):
    """Devuelve set de paginas maqueta a las que pertenece este producto."""
    paginas = set()
    for cat in producto_limpio["categorias"]:
        for pagina in WP_CAT_TO_PAGINA.get(cat["id"], []):
            paginas.add(pagina)
    return paginas

if __name__ == "__main__":
    print("Bajando todo el catalogo de victtorino.cl...")
    raw = bajar_todos_productos()
    print(f"\n=> {len(raw)} productos totales bajados\n")

    # Limpiar todos
    productos = [limpiar(p) for p in raw]

    # Agrupar por pagina maqueta (con dedupe por id)
    por_pagina = defaultdict(dict)  # slug_pagina -> {id_producto: producto}
    sin_pagina = []
    for p in productos:
        paginas = asignar_a_paginas(p)
        if not paginas:
            sin_pagina.append(p)
            continue
        for pagina in paginas:
            por_pagina[pagina][p["id"]] = p

    # Escribir cada pagina (incluso vacias)
    print("=== ARCHIVOS GENERADOS ===")
    for slug in PAGINAS:
        productos_pagina = list(por_pagina.get(slug, {}).values())
        out_file = OUT_DIR / f"{slug}.json"
        payload = {
            "categoria_pagina": slug,
            "total_productos": len(productos_pagina),
            "productos": productos_pagina,
        }
        out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        size_kb = out_file.stat().st_size / 1024
        print(f"  {slug:20s}  {len(productos_pagina):3d} productos  {size_kb:7.1f} KB  -> {out_file.name}")

    # Resumen y warnings
    print()
    print(f"=== RESUMEN ===")
    print(f"  Productos en al menos una pagina: {sum(len(v) for v in por_pagina.values())} (con duplicacion entre paginas)")
    print(f"  Productos unicos asignados:        {len({p['id'] for v in por_pagina.values() for p in v.values()})}")
    print(f"  Productos sin pagina maqueta:      {len(sin_pagina)}")
    if sin_pagina:
        print(f"\n  WARN: estos productos no calzaron en ningun mapeo:")
        for p in sin_pagina[:10]:
            cats = ", ".join(c["name"] for c in p["categorias"]) or "(sin categorias)"
            print(f"    [{p['id']}] {p['name'][:60]:60s}  cats=[{cats}]")
        if len(sin_pagina) > 10:
            print(f"    ... +{len(sin_pagina)-10} mas")
