"""
Cruza el catalogo de la app alila con el inventario de Victor (Defontana/ML) y calcula margenes.
Salida: alila_cruce_margen.xlsx
"""
import pandas as pd, re, json
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
CNY_CLP = 130.9  # tipo de cambio CNY->CLP (open.er-api.com, 2026-06-04)

# ---------- cargar ----------
al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
mt = pd.read_excel(ROOT / "matching_defontana_ml_2026-05-26.xlsx", sheet_name="MATCHED")

STOP = set("de la el los las y o con para por sin un una set kit pack cm mm para mas más x color "
           "negro blanco acero inoxidable t- repuesto the of and a in to".split())
def toks(s):
    if not isinstance(s, str): return set()
    w = re.findall(r"[a-záéíóúñ]{4,}", s.lower())
    return {t for t in w if t not in STOP}

# ---------- 1) CRUCE por texto ----------
# universo Victor: titulo ML + descripcion defontana
mt["victor_txt"] = (mt["title_ml"].fillna("") + " " + mt["descripcion_defontana"].fillna(""))
mt["vtok"] = mt["victor_txt"].apply(toks)
# texto alila en español: keywords ES + categoria ES + nombre EN
al["alila_txt"] = (al.get("Keywords ES", "").fillna("") + " " + al.get("Categoría ES", "").fillna("")
                   + " " + al.get("Nombre (EN)", "").fillna("").astype(str))
al["atok"] = al["alila_txt"].apply(toks)

matches = []
al_tok_list = list(al["atok"])
for _, vr in mt.iterrows():
    vt = vr["vtok"]
    if len(vt) < 2: continue
    best, bi = 0.0, -1
    for i, at in enumerate(al_tok_list):
        if not at: continue
        inter = len(vt & at)
        if inter < 2: continue
        j = inter / len(vt | at)
        if j > best:
            best, bi = j, i
    if best >= 0.35 and bi >= 0:
        ar = al.iloc[bi]
        matches.append({
            "Victor_item_ML": vr["item_id"], "Victor_titulo": vr["title_ml"],
            "Victor_costo": vr["costo_vigente"], "Victor_precio_ML": vr["price_ml"],
            "similitud": round(best, 2),
            "alila_codigo": ar["Código"], "alila_keywords": str(ar.get("Keywords ES", ""))[:80],
            "alila_costo_CNY": ar.get("Costo compra"),
            "alila_costo_CLP": round((ar.get("Costo compra") or 0) * CNY_CLP) if pd.notna(ar.get("Costo compra")) else None,
            "alila_precio_CLP": ar.get("Precio (1u/menor cant.)"),
        })
cruce = pd.DataFrame(matches).sort_values("similitud", ascending=False) if matches else pd.DataFrame()

# ---------- 2) MARGEN del catalogo alila ----------
m = al.copy()
m["Costo CLP (cgj)"] = (pd.to_numeric(m["Costo compra"], errors="coerce") * CNY_CLP).round()
m["Precio venta CLP"] = pd.to_numeric(m["Precio (1u/menor cant.)"], errors="coerce")
m["Margen CLP"] = (m["Precio venta CLP"] - m["Costo CLP (cgj)"]).round()
m["Margen %"] = ((m["Margen CLP"] / m["Precio venta CLP"]) * 100).round(1)
m["Markup x"] = (m["Precio venta CLP"] / m["Costo CLP (cgj)"]).round(2)
cols_m = ["Código", "Nombre (EN)", "Estado", "Categoría ES", "Costo compra", "Costo CLP (cgj)",
          "Precio venta CLP", "Precio (mayor cant.)", "Margen CLP", "Margen %", "Markup x",
          "Link proveedor (1688)", "Link MercadoLibre", "N° fotos", "Foto principal"]
cols_m = [c for c in cols_m if c in m.columns]
margen = m[cols_m].copy()
# solo productos en venta CON costo y precio validos (los de costo 0 son datos faltantes -> ruido)
valido = (margen["Estado"] == "上线销售") & (margen["Costo CLP (cgj)"] > 0) & (margen["Precio venta CLP"] > 0)
margen_venta = margen[valido].sort_values("Margen CLP", ascending=False)
sin_costo = int(((margen["Estado"] == "上线销售") & ~(margen["Costo CLP (cgj)"] > 0)).sum())

# ---------- 3) CERCA DE TU LINEA (baño / cocina / hogar) ----------
pat = re.compile(r"ba[ñn]o|cocina|menaje|hogar|sanitari|grifer|llave|ducha|lavaplatos|organizador", re.I)
cerca = margen_venta[margen_venta["Categoría ES"].fillna("").str.contains(pat)]

# ---------- escribir ----------
out = ROOT / "alila_cruce_margen.xlsx"
with pd.ExcelWriter(out, engine="xlsxwriter") as w:
    resumen = pd.DataFrame({
        "métrica": ["Productos alila (total)", "alila en venta", "En venta con costo válido",
                    "En venta SIN costo cargado", "Tipo cambio CNY->CLP",
                    "Margen % mediano (costo válido)", "Margen CLP mediano",
                    "Productos cerca de tu línea (baño/cocina/hogar)",
                    "Coincidencias de texto con tu inventario (sim>=0.35)"],
        "valor": [len(al), int((al["Estado"] == "上线销售").sum()), len(margen_venta), sin_costo, CNY_CLP,
                  round(margen_venta["Margen %"].median(), 1), int(margen_venta["Margen CLP"].median()),
                  len(cerca), len(cruce)],
    })
    resumen.to_excel(w, sheet_name="RESUMEN", index=False)
    margen_venta.to_excel(w, sheet_name="MARGEN_ALILA", index=False)
    cerca.to_excel(w, sheet_name="CERCA_DE_TU_LINEA", index=False)
    (cruce if len(cruce) else pd.DataFrame({"info": ["Sin coincidencias relevantes: catálogos disjuntos"]})).to_excel(w, sheet_name="CRUCE_INVENTARIO", index=False)

print("=== LISTO ->", out, "===")
print("alila en venta:", int((al["Estado"] == "上线销售").sum()), "| con costo válido:", len(margen_venta), "| sin costo:", sin_costo)
print("Margen % mediano:", round(margen_venta["Margen %"].median(), 1), "| Margen CLP mediano:", int(margen_venta["Margen CLP"].median()))
print("Coincidencias texto con tu inventario:", len(cruce))
print("Cerca de tu línea (baño/cocina/hogar):", len(cerca))
print("\nTop 10 por MARGEN CLP (en venta, costo válido):")
print(margen_venta.head(10)[["Código", "Categoría ES", "Costo CLP (cgj)", "Precio venta CLP", "Margen CLP", "Margen %"]].to_string(index=False))
print("\nTop 8 'cerca de tu línea' por margen CLP:")
print(cerca.sort_values("Margen CLP", ascending=False).head(8)[["Código", "Categoría ES", "Costo CLP (cgj)", "Precio venta CLP", "Margen CLP", "Margen %"]].to_string(index=False))
if len(cruce):
    print("\nMuestra cruce con tu inventario:")
    print(cruce.head(6)[["Victor_titulo", "alila_keywords", "similitud", "Victor_costo", "alila_costo_CLP"]].to_string(index=False))
