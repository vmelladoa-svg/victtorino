"""
Bloque 1 — Extraccion y filtrado de catalogo desde WooCommerce.
Lee los 270 SKUs activos de victtorino.cl, aplica filtros, escribe CSV.

Output: data/catalogo_instagram.csv
"""
import sys
import io
import csv
import time
import requests
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

WC_BASE = "https://victtorino.cl"
WC_KEY = "ck_b288c68a7cd7d3c536e31bd68e44795276809aa7"
WC_SEC = "cs_2e3efe702d9dc28eec992a344050bcfc157bf901"

CATEGORIAS_ASPIRACIONALES = {
    "Griferia", "Grifería",
    "Lavaplatos",
    "Espejos",
    "Lavamanos",
    "Shower/Mamparas/Receptaculos", "Shower/Mamparas/Receptáculos",
}

PRECIO_MIN = 20_000
PRECIO_MAX = 150_000
STOCK_MIN = 5


def bajar_todos_productos():
    """Pagina todos los productos publicados de WooCommerce."""
    out = []
    page = 1
    while True:
        r = requests.get(
            f"{WC_BASE}/wp-json/wc/v3/products",
            params={"per_page": 100, "status": "publish", "page": page},
            auth=(WC_KEY, WC_SEC), timeout=30,
        )
        if r.status_code != 200:
            print(f"  ERR HTTP {r.status_code} en page {page}: {r.text[:120]}")
            break
        chunk = r.json()
        if not chunk: break
        out.extend(chunk)
        print(f"  page {page}: {len(chunk)} prods (acum {len(out)})")
        if len(chunk) < 100: break
        page += 1
        time.sleep(0.3)
    return out


def categoria_principal(p):
    cats = [c["name"] for c in (p.get("categories") or [])]
    return cats[0] if cats else ""


def primera_imagen(p):
    imgs = p.get("images") or []
    return imgs[0]["src"] if imgs else ""


def precio_num(p):
    """Devuelve int del precio (regular o sale)."""
    raw = p.get("regular_price") or p.get("price") or "0"
    try: return int(float(raw))
    except: return 0


def stock_num(p):
    """Devuelve cantidad numerica de stock (0 si no se sabe)."""
    sq = p.get("stock_quantity")
    if sq is not None:
        try: return int(sq)
        except: return 0
    return 0


def calc_score(p):
    """Aplica los 5 filtros y devuelve (score 0-5, list[reasons])."""
    score = 0
    reasons = []
    razones_no = []

    # 1) Precio entre 20k y 150k
    precio = precio_num(p)
    if PRECIO_MIN <= precio <= PRECIO_MAX:
        score += 1; reasons.append(f"precio_ok({precio})")
    else:
        razones_no.append(f"precio_fuera_rango({precio})")

    # 2) Stock >= 5
    stk = stock_num(p)
    if stk >= STOCK_MIN:
        score += 1; reasons.append(f"stock_ok({stk})")
    else:
        razones_no.append(f"stock_bajo({stk})")

    # 3) >= 1 imagen
    if (p.get("images") or []):
        score += 1; reasons.append("foto_ok")
    else:
        razones_no.append("sin_foto")

    # 4) Categoria aspiracional
    cats = {c["name"] for c in (p.get("categories") or [])}
    if cats & CATEGORIAS_ASPIRACIONALES:
        score += 1; reasons.append(f"cat_aspiracional({','.join(cats & CATEGORIAS_ASPIRACIONALES)})")
    else:
        razones_no.append(f"cat_no_aspiracional({categoria_principal(p)})")

    # 5) Margen >= 25%
    # WC no expone costo y el Defontana cargado es mock (15 SKUs VIC-xxx demo).
    # Usamos margen ESTIMADO por categoria basado en promedio Defontana real:
    #   - Categorias aspiracionales (Griferia, Lavaplatos, Espejos, etc.) -> 47%
    #   - Resto -> 35%
    # Se marca claramente como estimacion para revision manual.
    costo = None
    for md in (p.get("meta_data") or []):
        if md.get("key") in ("_wc_cog_cost", "_cost_of_goods", "costo"):
            try: costo = float(md.get("value") or 0)
            except: pass
            break

    if costo and precio:
        margen = (precio - costo) / precio
        if margen >= 0.25:
            score += 1; reasons.append(f"margen_ok_real({margen:.0%})")
        else:
            razones_no.append(f"margen_bajo_real({margen:.0%})")
    else:
        # Estimacion por categoria
        margen_est = 0.47 if (cats & CATEGORIAS_ASPIRACIONALES) else 0.35
        if margen_est >= 0.25:
            score += 1
            reasons.append(f"margen_estimado({margen_est:.0%}_revisar)")
        else:
            razones_no.append(f"margen_estimado_bajo({margen_est:.0%})")

    razon_total = " | ".join(reasons + razones_no)
    return score, razon_total


def main():
    print("=== Bloque 1: Extraccion y filtrado de catalogo Woo ===\n")
    print("Bajando productos de WooCommerce...")
    prods = bajar_todos_productos()
    print(f"\nTotal productos publicados: {len(prods)}\n")

    # Analizar
    rows = []
    cats_count = Counter()
    for p in prods:
        score, reason = calc_score(p)
        cats_count[categoria_principal(p)] += 1
        rows.append({
            "sku": p.get("sku") or "",
            "name": p.get("name") or "",
            "slug": p.get("slug") or "",
            "price": precio_num(p),
            "stock": stock_num(p),
            "category": categoria_principal(p),
            "image_url": primera_imagen(p),
            "product_url": p.get("permalink") or "",
            "pass_filter": score >= 3,
            "filter_score": score,
            "reason": reason,
        })

    # HARD RULE: solo productos con stock > 0 (regla obligatoria del negocio).
    # Si stock = 0, pass_filter = False sin importar el score.
    for r in rows:
        if r["stock"] == 0:
            r["pass_filter"] = False
            r["reason"] = "BLOQUEADO_STOCK_0 | " + r["reason"]

    # Ordenar por score desc, precio desc
    rows.sort(key=lambda r: (-r["filter_score"], -r["price"]))

    # Escribir CSV
    out_csv = DATA_DIR / "catalogo_instagram.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"CSV escrito: {out_csv}\n")

    # Resumen
    aprobados = [r for r in rows if r["pass_filter"]]
    print("====== RESUMEN ======")
    print(f"Total SKUs publicados:  {len(rows)}")
    print(f"Candidatos aprobados (>=3/5):  {len(aprobados)}")
    print(f"\nDistribucion de scores:")
    for sc in range(6):
        cnt = sum(1 for r in rows if r["filter_score"] == sc)
        print(f"  score {sc}: {cnt}")
    print(f"\nCategorias presentes:")
    for cat, n in cats_count.most_common():
        marca = "  *" if cat in CATEGORIAS_ASPIRACIONALES else "   "
        print(f"  {marca} {cat}: {n}")
    print()
    print("Top 10 candidatos por score:")
    print(f"  {'SKU':<14} {'Score':>5} {'Precio':>9} {'Stock':>6} {'Categoria':<22} Nombre")
    for r in aprobados[:10]:
        print(f"  {r['sku']:<14} {r['filter_score']:>5} ${r['price']:>7,} {r['stock']:>6} "
              f"{r['category']:<22} {r['name'][:50]}")


if __name__ == "__main__":
    main()
