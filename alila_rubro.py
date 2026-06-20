"""
Oportunidades en el RUBRO de Victor (baño/cocina/sanitario/gasfitería) con
margen + competencia ML + stock alila. Agrega hoja 'MI_RUBRO' al xlsx.
"""
import alila_app_client as A
import pandas as pd, re, json, time
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
CNY_CLP = 130.9
XLS = ROOT / "alila_oportunidades.xlsx"

al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
cache = json.load(open(ROOT / "alila_precio_mercado.json", encoding="utf-8"))
def eid(u):
    if not isinstance(u, str): return None
    m = re.search(r'/p/(MLC\d+)', u) or re.search(r'/up/(MLCU\d+)', u); return m.group(1) if m else None
al["mkt_id"] = al["Link MercadoLibre"].apply(eid)
al["Precio mercado ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("precio_min") if i else None)
al["N° ofertas ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("n_ofertas") if i else None)
al["Costo 1688 CLP"] = (pd.to_numeric(al["Costo compra"], errors="coerce") * CNY_CLP).round()
al["Precio alila CLP"] = pd.to_numeric(al["Precio (1u/menor cant.)"], errors="coerce")
mkt = pd.to_numeric(al["Precio mercado ML"], errors="coerce")
al["Margen vs alila CLP"] = (mkt - al["Precio alila CLP"]).round()
al["Margen vs alila %"] = ((al["Margen vs alila CLP"] / mkt) * 100).round(1)
al["Margen vs 1688 %"] = (((mkt - al["Costo 1688 CLP"]) / mkt) * 100).round(1)

# rubro: incluir baño/cocina/gasfiteria; excluir bebés y juegos
inc = re.compile(r"(Hogar y Muebles>Baños|Cocina y Menaje|Mobiliario para (Baños|Cocinas)|Gasfiter|Hornos y Cocinas|Accesorios de Construcción)", re.I)
exc = re.compile(r"Bebés|Juegos", re.I)
cat = al["Categoría ES"].fillna("")
rub = al[(al["Estado"] == "上线销售") & mkt.notna() & cat.str.contains(inc) & ~cat.str.contains(exc)].copy()

# stock
A.auth()
def stock(hjh):
    try:
        d = (A.coll_get("spkc", where={"hjh": int(hjh)}, limit=1).get("data") or {}).get("data") or []
        return d[0].get("zl_kc") if d else None
    except Exception:
        return None
sk = []
for k, c in enumerate(rub["Código"], 1):
    if k % 50 == 0: A.auth()
    sk.append(stock(c)); time.sleep(0.05)
rub["Stock alila"] = sk

# nombre legible desde slug ML
def slug(u):
    if not isinstance(u, str): return None
    s = u.split("#")[0].split("?")[0]
    m = re.search(r'mercadolibre\.cl/([a-z0-9\-]+)/(?:p|up)/MLC', s) or re.search(r'articulo\.mercadolibre\.cl/MLC-?\d+-([a-z0-9\-]+?)-?_JM', s)
    if not m: return None
    t = m.group(1).replace("-", " ").strip(); return t[:1].upper() + t[1:]
rub["Nombre ES"] = rub.apply(lambda r: slug(r["Link MercadoLibre"]) or r.get("Nombre (EN)") or "", axis=1)

cols = ["Código", "Nombre ES", "Categoría ES", "N° ofertas ML", "Stock alila",
        "Costo 1688 CLP", "Precio alila CLP", "Precio mercado ML",
        "Margen vs alila CLP", "Margen vs alila %", "Margen vs 1688 %",
        "Link proveedor (1688)", "Link MercadoLibre", "N° fotos", "Foto principal"]
rub = rub[[c for c in cols if c in rub.columns]]

# clasificacion
rub["_disp"] = rub["Stock alila"].fillna(-1)
ganadoras = rub[(rub["N° ofertas ML"] <= 6) & (rub["Margen vs alila %"] >= 35) &
                (rub["Margen vs alila CLP"] >= 8000) & (rub["_disp"] > 0)].sort_values("Margen vs alila CLP", ascending=False)
todo = rub.drop(columns="_disp").sort_values(["Margen vs alila CLP"], ascending=False)
ganadoras = ganadoras.drop(columns="_disp")

# escribir: añadir hojas al xlsx existente
sheets = pd.read_excel(XLS, sheet_name=None)
sheets["MI_RUBRO_GANADORAS"] = ganadoras
sheets["MI_RUBRO_TODO"] = todo
with pd.ExcelWriter(XLS, engine="xlsxwriter") as w:
    for n, d in sheets.items():
        d.to_excel(w, sheet_name=n[:31], index=False)

print(f"Rubro (baño/cocina/gasfitería) con precio de mercado: {len(rub)}")
print(f"GANADORAS (≤6 ofertas, margen≥35% y ≥8k, CON stock): {len(ganadoras)}")
print("\nGanadoras de tu rubro:")
print(ganadoras.head(20)[["Código", "Nombre ES", "Categoría ES", "N° ofertas ML", "Stock alila", "Precio alila CLP", "Precio mercado ML", "Margen vs alila %"]].to_string(index=False))
