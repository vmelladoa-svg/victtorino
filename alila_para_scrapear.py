"""
Genera la lista de complementarios baño/cocina que NO tienen precio de mercado vía API,
para que un navegador (Claude con Chrome) abra el link y anote el precio.
Salida: alila_complementarios_sin_precio.xlsx (+ .csv) con link directo y columna 'Precio ML (llenar)'.
"""
import pandas as pd, re, json
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
CNY_CLP = 130.9
al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
cache = json.load(open(ROOT / "alila_precio_mercado.json", encoding="utf-8"))

def eid(u):
    if not isinstance(u, str): return None
    m = re.search(r'/p/(MLC\d+)', u) or re.search(r'/up/(MLCU\d+)', u); return m.group(1) if m else None
def slug(u):
    if not isinstance(u, str): return None
    s = u.split("#")[0].split("?")[0]
    m = re.search(r'mercadolibre\.cl/([a-z0-9\-]+)/(?:p|up)/MLC', s) or re.search(r'articulo\.mercadolibre\.cl/MLC-?\d+-([a-z0-9\-]+?)-?_JM', s)
    if not m: return None
    t = m.group(1).replace("-", " ").strip(); return t[:1].upper() + t[1:]

al["mkt_id"] = al["Link MercadoLibre"].apply(eid)
al["tiene_precio_api"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("status") == 200 if i else False)
al["Costo 1688 CLP"] = (pd.to_numeric(al["Costo compra"], errors="coerce") * CNY_CLP).round()
al["Precio alila CLP"] = pd.to_numeric(al["Precio (1u/menor cant.)"], errors="coerce")

cat = al["Categoría ES"].fillna("")
comp = al[(al["Estado"] == "上线销售") &
          cat.str.contains(r"Cocina y Menaje|Hogar y Muebles>Baños|Mobiliario para Baños|Mobiliario para Cocinas")].copy()

# necesitan precio: tienen link ML pero no se pudo por API
link = comp["Link MercadoLibre"].fillna("")
falta = comp[(~comp["tiene_precio_api"]) & (link.str.startswith("http"))].copy()
falta["Nombre ES"] = falta.apply(lambda r: slug(r["Link MercadoLibre"]) or r.get("Nombre (EN)") or "(revisar foto)", axis=1)

out = falta[["Código", "Nombre ES", "Categoría ES", "Costo 1688 CLP", "Precio alila CLP", "Link MercadoLibre"]].copy()
out.insert(5, "Precio ML (llenar)", "")   # columna para que el navegador complete
out = out.sort_values("Categoría ES")

dest = ROOT / "alila_complementarios_sin_precio.xlsx"
out.to_excel(dest, index=False)
out.to_csv(ROOT / "alila_complementarios_sin_precio.csv", index=False, encoding="utf-8-sig")
print(f"Productos complementarios SIN precio API pero con link ML: {len(out)}")
print(f"-> {dest.name} (+ .csv)")
print("\nSon estos (abrir link, anotar precio publicado):")
print(out[["Código", "Nombre ES", "Link MercadoLibre"]].head(40).to_string(index=False))
