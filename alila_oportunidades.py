"""
Lista de OPORTUNIDADES: productos alila con baja competencia en ML + margen sano.
Filtra el catalogo+precio de mercado y rankea por score = margen CLP / n_ofertas.
Salida: alila_oportunidades.xlsx
"""
import json, re, pandas as pd
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
CNY_CLP = 130.9

al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
cache = json.load(open(ROOT / "alila_precio_mercado.json", encoding="utf-8"))

def eid(u):
    if not isinstance(u, str): return None
    m = re.search(r'/p/(MLC\d+)', u) or re.search(r'/up/(MLCU\d+)', u)
    return m.group(1) if m else None

al["mkt_id"] = al["Link MercadoLibre"].apply(eid)
al["Precio mercado ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("precio_min") if i else None)
al["N° ofertas ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("n_ofertas") if i else None)

al["Costo 1688 CLP"] = (pd.to_numeric(al["Costo compra"], errors="coerce") * CNY_CLP).round()
al["Precio alila CLP"] = pd.to_numeric(al["Precio (1u/menor cant.)"], errors="coerce")
mkt = pd.to_numeric(al["Precio mercado ML"], errors="coerce")
al["Margen vs alila CLP"] = (mkt - al["Precio alila CLP"]).round()
al["Margen vs alila %"] = ((al["Margen vs alila CLP"] / mkt) * 100).round(1)
al["Margen vs 1688 CLP"] = (mkt - al["Costo 1688 CLP"]).round()
al["Margen vs 1688 %"] = ((al["Margen vs 1688 CLP"] / mkt) * 100).round(1)
al["Score (margen/competencia)"] = (al["Margen vs alila CLP"] / al["N° ofertas ML"]).round()

base = al[(al["Estado"] == "上线销售") & mkt.notna()].copy()

cols = ["Código", "Nombre (EN)", "Categoría ES", "Keywords ES",
        "N° ofertas ML", "Costo 1688 CLP", "Precio alila CLP", "Precio mercado ML",
        "Margen vs alila CLP", "Margen vs alila %", "Margen vs 1688 CLP", "Margen vs 1688 %",
        "Score (margen/competencia)", "Link proveedor (1688)", "Link MercadoLibre",
        "N° fotos", "Foto principal"]
cols = [c for c in cols if c in base.columns]
base = base[cols]

# --- OPORTUNIDADES: baja competencia (2-5 ofertas) + margen sano ---
op = base[(base["N° ofertas ML"].between(2, 5)) &
          (base["Margen vs alila %"] >= 40) &
          (base["Margen vs alila CLP"] >= 10000)].sort_values("Score (margen/competencia)", ascending=False)

# --- TOP 50 shortlist ---
top = op.head(50)

# --- MONOPOLIO: 1 sola oferta (alto riesgo/recompensa, precio dudoso) ---
mono = base[(base["N° ofertas ML"] == 1) & (base["Margen vs alila CLP"] >= 15000)].sort_values("Margen vs alila CLP", ascending=False)

# --- CERCA DE TU LÍNEA dentro de oportunidades ---
pat = re.compile(r"ba[ñn]o|cocina|menaje|hogar|grifer|llave|ducha|organizador|mueble", re.I)
cerca = op[op["Categoría ES"].fillna("").str.contains(pat)]

dest = ROOT / "alila_oportunidades.xlsx"
with pd.ExcelWriter(dest, engine="xlsxwriter") as w:
    pd.DataFrame({
        "métrica": ["Universo (en venta con precio mercado)", "OPORTUNIDADES (2-5 ofertas, margen≥40% y ≥10k)",
                    "  -> de esas, cerca de tu línea (hogar/cocina)", "Monopolio (1 sola oferta, margen≥15k)",
                    "Margen vs alila mediano en oportunidades (%)", "Margen vs alila mediano en oportunidades (CLP)"],
        "valor": [len(base), len(op), len(cerca), len(mono),
                  round(op["Margen vs alila %"].median(), 1) if len(op) else 0,
                  int(op["Margen vs alila CLP"].median()) if len(op) else 0],
    }).to_excel(w, sheet_name="RESUMEN", index=False)
    top.to_excel(w, sheet_name="TOP_50", index=False)
    op.to_excel(w, sheet_name="OPORTUNIDADES", index=False)
    cerca.to_excel(w, sheet_name="CERCA_DE_TU_LINEA", index=False)
    mono.to_excel(w, sheet_name="MONOPOLIO_1_OFERTA", index=False)

print("=== LISTO ->", dest, "===")
print(f"Universo: {len(base)} | OPORTUNIDADES: {len(op)} | cerca de tu línea: {len(cerca)} | monopolio 1 oferta: {len(mono)}")
if len(op):
    print(f"Margen mediano en oportunidades: {round(op['Margen vs alila %'].median(),1)}% / {int(op['Margen vs alila CLP'].median())} CLP")
    print("\nTOP 15 oportunidades (baja competencia + margen sano):")
    print(top.head(15)[["Código", "Nombre (EN)", "Categoría ES", "N° ofertas ML", "Precio alila CLP", "Precio mercado ML", "Margen vs alila %", "Score (margen/competencia)"]].to_string(index=False))
