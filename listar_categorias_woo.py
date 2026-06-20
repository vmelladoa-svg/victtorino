"""Lista todas las categorias de productos en WooCommerce victtorino.cl."""
import json
import requests
from pathlib import Path

WC_URL = "https://victtorino.cl"
WC_KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
WC_SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

OUT_DIR = Path("data/maqueta")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def listar_categorias():
    cats = []
    page = 1
    while True:
        r = requests.get(
            f"{WC_URL}/wp-json/wc/v3/products/categories",
            params={"per_page": 100, "page": page, "hide_empty": False, "orderby": "name", "order": "asc"},
            auth=(WC_KEY, WC_SEC),
            timeout=60,
        )
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:300]}")
            break
        data = r.json()
        if not data:
            break
        cats.extend(data)
        total_pages = int(r.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return cats

def limpiar(cat):
    return {
        "id": cat["id"],
        "name": cat["name"],
        "slug": cat["slug"],
        "parent": cat["parent"],
        "count": cat["count"],
        "description": (cat.get("description") or "").strip(),
        "image": (cat.get("image") or {}).get("src") if cat.get("image") else None,
    }

if __name__ == "__main__":
    raw = listar_categorias()
    cats = [limpiar(c) for c in raw]
    out = OUT_DIR / "categorias.json"
    out.write_text(json.dumps(cats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(cats)} categorias guardadas en {out}")
    print()
    print("=== TOP-LEVEL (parent=0) ===")
    for c in sorted([x for x in cats if x["parent"] == 0], key=lambda x: -x["count"]):
        print(f"  [{c['id']:5d}]  count={c['count']:4d}  {c['name']:40s}  slug={c['slug']}")
    print()
    print("=== TOTAL ===", len(cats), "categorias")
