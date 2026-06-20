"""
Fusiona el precio de mercado ML (alila_precio_mercado.json) con el catalogo alila
y calcula el margen de REVENTA real:
  - comprando a alila (precio pf) y vendiendo al precio de mercado ML
  - comprando directo en 1688 (cgj->CLP) y vendiendo al precio de mercado ML
Salida: alila_margen_reventa.xlsx
"""
import json, re, pandas as pd
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
CNY_CLP = 130.9

al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
cache = json.loads((ROOT / "alila_precio_mercado.json").read_text())

def eid(u):
    if not isinstance(u, str): return None
    m = re.search(r'/p/(MLC\d+)', u) or re.search(r'/up/(MLCU\d+)', u)
    return m.group(1) if m else None

al["mkt_id"] = al["Link MercadoLibre"].apply(eid)
al["Precio mercado ML (min)"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("precio_min") if i else None)
al["Precio mercado ML (mediano)"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("precio_mediano") if i else None)
al["N° ofertas ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("n_ofertas") if i else None)

al["Costo 1688 CLP"] = (pd.to_numeric(al["Costo compra"], errors="coerce") * CNY_CLP).round()
al["Precio alila CLP"] = pd.to_numeric(al["Precio (1u/menor cant.)"], errors="coerce")
mkt = pd.to_numeric(al["Precio mercado ML (min)"], errors="coerce")

al["Margen reventa (compra alila) CLP"] = (mkt - al["Precio alila CLP"]).round()
al["Margen reventa (compra alila) %"] = ((al["Margen reventa (compra alila) CLP"] / mkt) * 100).round(1)
al["Margen reventa (1688 directo) CLP"] = (mkt - al["Costo 1688 CLP"]).round()
al["Margen reventa (1688 directo) %"] = ((al["Margen reventa (1688 directo) CLP"] / mkt) * 100).round(1)

cols = ["Código", "Nombre (EN)", "Estado", "Categoría ES",
        "Costo 1688 CLP", "Precio alila CLP", "Precio mercado ML (min)", "Precio mercado ML (mediano)", "N° ofertas ML",
        "Margen reventa (compra alila) CLP", "Margen reventa (compra alila) %",
        "Margen reventa (1688 directo) CLP", "Margen reventa (1688 directo) %",
        "Link proveedor (1688)", "Link MercadoLibre", "N° fotos", "Foto principal"]
cols = [c for c in cols if c in al.columns]
out = al[cols].copy()

con_mkt = out[mkt.notna() & (out["Estado"] == "上线销售")].copy()
# orden por margen de reventa comprando a alila
con_mkt = con_mkt.sort_values("Margen reventa (compra alila) CLP", ascending=False)
# ganadores reales: margen positivo comprando a alila
ganan = con_mkt[con_mkt["Margen reventa (compra alila) CLP"] > 0]
# cerca de tu linea
pat = re.compile(r"ba[ñn]o|cocina|menaje|hogar|sanitari|grifer|llave|ducha|lavaplatos|organizador|mueble", re.I)
cerca = con_mkt[con_mkt["Categoría ES"].fillna("").str.contains(pat)]

dest = ROOT / "alila_margen_reventa.xlsx"
with pd.ExcelWriter(dest, engine="xlsxwriter") as w:
    resumen = pd.DataFrame({
        "métrica": ["Productos en venta", "Con precio de mercado ML", "Sin precio (item directo, sin API)",
                    "Tipo cambio CNY->CLP",
                    "Margen reventa comprando a alila — mediano %", "Margen reventa comprando a alila — mediano CLP",
                    "Productos rentables comprando a alila (margen>0)",
                    "Margen reventa 1688 directo — mediano %",
                    "Cerca de tu línea (hogar/cocina/muebles) con precio"],
        "valor": [int((al["Estado"] == "上线销售").sum()), int(con_mkt.shape[0]),
                  int(((al["Estado"] == "上线销售") & mkt.isna()).sum()), CNY_CLP,
                  round(con_mkt["Margen reventa (compra alila) %"].median(), 1),
                  int(con_mkt["Margen reventa (compra alila) CLP"].median()),
                  int(ganan.shape[0]),
                  round(con_mkt["Margen reventa (1688 directo) %"].median(), 1),
                  int(cerca.shape[0])],
    })
    resumen.to_excel(w, sheet_name="RESUMEN", index=False)
    con_mkt.to_excel(w, sheet_name="MARGEN_REVENTA", index=False)
    ganan.to_excel(w, sheet_name="RENTABLES_VIA_ALILA", index=False)
    cerca.to_excel(w, sheet_name="CERCA_DE_TU_LINEA", index=False)

print("=== LISTO ->", dest, "===")
print("En venta:", int((al["Estado"] == "上线销售").sum()), "| con precio mercado:", con_mkt.shape[0])
print("Margen reventa (compra alila) mediano:", round(con_mkt["Margen reventa (compra alila) %"].median(), 1), "% /",
      int(con_mkt["Margen reventa (compra alila) CLP"].median()), "CLP")
print("Rentables comprando a alila (margen>0):", ganan.shape[0])
print("Margen reventa 1688 directo mediano:", round(con_mkt["Margen reventa (1688 directo) %"].median(), 1), "%")
print("\nTop 10 margen reventa CLP (comprando a alila):")
print(con_mkt.head(10)[["Código", "Categoría ES", "Precio alila CLP", "Precio mercado ML (min)", "N° ofertas ML", "Margen reventa (compra alila) CLP", "Margen reventa (compra alila) %"]].to_string(index=False))
