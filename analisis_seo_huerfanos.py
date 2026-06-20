"""
Detecta productos del catálogo con SEO incompleto:
- sin focus keyword
- sin meta_title personalizado de Rank Math
- sin meta_description personalizada
- descripción muy corta (<200 palabras)
"""
import json
import sys
import io
import re
import requests
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

print("[1/2] Cargando todos los productos publish...")
productos = []
page = 1
while True:
    r = requests.get(f"{WC}/wp-json/wc/v3/products",
                     params={**P, "per_page": 100, "page": page, "status": "publish"},
                     timeout=30)
    if r.status_code != 200:
        break
    d = r.json()
    if not d:
        break
    productos.extend(d)
    if int(r.headers.get("X-WP-TotalPages", 1)) <= page:
        break
    page += 1
print(f"      total: {len(productos)} productos publish\n")

# Análisis
print("[2/2] Analizando SEO de cada producto...")
sin_focus = []
sin_meta_title = []
sin_meta_desc = []
desc_corta = []  # <200 palabras
desc_muy_corta = []  # <100 palabras
sin_imagenes = []
seo_completo = []

por_cat_huerfanos = Counter()

for p in productos:
    meta = {m["key"]: m["value"] for m in p.get("meta_data", []) if "rank_math" in m["key"]}
    focus = meta.get("rank_math_focus_keyword", "").strip()
    mt = meta.get("rank_math_title", "").strip()
    md = meta.get("rank_math_description", "").strip()
    plain = re.sub(r"<[^>]+>", " ", p.get("description", ""))
    palabras = len(plain.split())
    imgs = len(p.get("images", []))
    cats = [c["name"] for c in p.get("categories", [])]
    cat_principal = cats[0] if cats else "(sin)"

    info = {"id": p["id"], "name": p["name"], "cat": cat_principal,
            "focus": focus, "palabras": palabras, "imgs": imgs}

    flags = []
    if not focus:
        sin_focus.append(info); flags.append("sin_focus")
    if not mt:
        sin_meta_title.append(info); flags.append("sin_mt")
    if not md:
        sin_meta_desc.append(info); flags.append("sin_md")
    if palabras < 100:
        desc_muy_corta.append(info); flags.append("desc<100")
    elif palabras < 200:
        desc_corta.append(info); flags.append("desc<200")
    if imgs == 0:
        sin_imagenes.append(info); flags.append("sin_img")

    if not flags:
        seo_completo.append(info)
    else:
        if "sin_focus" in flags:  # criterio principal de "huérfano SEO"
            por_cat_huerfanos[cat_principal] += 1

print(f"\n{'=' * 80}")
print("REPORTE — Estado SEO del catálogo")
print(f"{'=' * 80}\n")
print(f"Total productos publish: {len(productos)}")
print(f"  Sin focus keyword:        {len(sin_focus):4} ({len(sin_focus)*100//len(productos)}%)")
print(f"  Sin meta_title:           {len(sin_meta_title):4} ({len(sin_meta_title)*100//len(productos)}%)")
print(f"  Sin meta_description:     {len(sin_meta_desc):4} ({len(sin_meta_desc)*100//len(productos)}%)")
print(f"  Descripción <100 palabras:{len(desc_muy_corta):4} ({len(desc_muy_corta)*100//len(productos)}%)")
print(f"  Descripción <200 palabras:{len(desc_corta):4}")
print(f"  Sin imágenes:             {len(sin_imagenes):4}")
print(f"  SEO completo:             {len(seo_completo):4} ({len(seo_completo)*100//len(productos)}%)")

print(f"\n## Productos SIN focus keyword por categoría destino")
print(f"{'Categoría':40} {'Cantidad'}")
print("-" * 60)
for cat, n in por_cat_huerfanos.most_common():
    print(f"  {cat[:38]:38} {n}")

print(f"\n## Productos sin focus + descripción <100 palabras (PRIORIDAD ALTA)")
print(f"   (estos necesitan plantilla SEO premium completa)\n")
sin_focus_y_corta = [p for p in sin_focus if p["palabras"] < 100]
print(f"   Total: {len(sin_focus_y_corta)}")
print(f"\n   Muestra (10 primeros):")
for p in sin_focus_y_corta[:10]:
    print(f"     {p['id']:5} [{p['cat'][:20]:20}] pal={p['palabras']:3} img={p['imgs']}  {p['name'][:50]}")

print(f"\n## Productos sin focus pero CON descripción decente (>=200 palabras)")
print(f"   (solo necesitan focus + meta tags, no reescritura)\n")
sin_focus_pero_largo = [p for p in sin_focus if p["palabras"] >= 200]
print(f"   Total: {len(sin_focus_pero_largo)}")

# Guardar
with open(r"C:\Users\dell\victtorino\analisis_seo_huerfanos.json", "w", encoding="utf-8") as f:
    json.dump({
        "total": len(productos),
        "sin_focus": [p["id"] for p in sin_focus],
        "sin_focus_detalle": sin_focus,
        "sin_focus_desc_corta": [p["id"] for p in sin_focus_y_corta],
        "sin_focus_desc_decente": [p["id"] for p in sin_focus_pero_largo],
        "sin_imagenes": [p["id"] for p in sin_imagenes],
        "seo_completo": len(seo_completo),
    }, f, ensure_ascii=False, indent=2)
print(f"\nDetalle en analisis_seo_huerfanos.json")
