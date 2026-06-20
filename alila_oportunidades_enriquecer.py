"""
Enriquece la lista de oportunidades con nombre legible en español (desde el slug del
link ML + respaldo API catalogo) y descarga la foto principal de cada una.
Salida: alila_oportunidades.xlsx (regenerado con columna 'Nombre ES') + carpeta alila_oportunidades_fotos/
"""
import json, re, requests, time, pandas as pd
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
IMGDIR = ROOT / "alila_oportunidades_fotos"
IMGDIR.mkdir(exist_ok=True)
CNY_CLP = 130.9
tok = json.load(open(ROOT / "tokens_cuenta3.json"))["access_token"]
HA = {"Authorization": f"Bearer {tok}"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}

def nombre_de_slug(u):
    if not isinstance(u, str): return None
    s = u.split("#")[0].split("?")[0]
    slug = None
    m = re.search(r'mercadolibre\.cl/([a-z0-9\-]+)/(?:p|up)/MLC', s)   # /p/ y /up/
    if m: slug = m.group(1)
    if not slug:
        m = re.search(r'articulo\.mercadolibre\.cl/MLC-?\d+-([a-z0-9\-]+?)-?_JM', s)  # articulo
        if m: slug = m.group(1)
    if not slug: return None
    txt = slug.replace("-", " ").strip()
    return txt[:1].upper() + txt[1:] if txt else None

def nombre_de_api(pid):
    try:
        r = requests.get(f"https://api.mercadolibre.com/products/{pid}", headers=HA, timeout=15)
        if r.status_code == 200:
            return r.json().get("name")
    except Exception:
        pass
    return None

def eid(u):
    if not isinstance(u, str): return None
    m = re.search(r'/p/(MLC\d+)', u) or re.search(r'/up/(MLCU\d+)', u)
    return m.group(1) if m else None

# ---- reconstruir oportunidades (mismo criterio) ----
al = pd.read_excel(ROOT / "alila_app_catalogo.xlsx")
cache = json.load(open(ROOT / "alila_precio_mercado.json", encoding="utf-8"))
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

op = base[(base["N° ofertas ML"].between(2, 5)) & (base["Margen vs alila %"] >= 40) &
          (base["Margen vs alila CLP"] >= 10000)].sort_values("Score (margen/competencia)", ascending=False)
mono = base[(base["N° ofertas ML"] == 1) & (base["Margen vs alila CLP"] >= 15000)].sort_values("Margen vs alila CLP", ascending=False)

# ---- nombre ES (slug -> api -> nombre alila) y foto, para op + mono ----
def enriquecer(df, bajar_foto):
    nombres, fotos = [], []
    for _, r in df.iterrows():
        nm = nombre_de_slug(r["Link MercadoLibre"]) or nombre_de_api(r["mkt_id"]) or r.get("Nombre (EN)") or ""
        nombres.append(nm)
        local = ""
        if bajar_foto:
            url = r.get("Foto principal")
            if isinstance(url, str) and url.startswith("http"):
                try:
                    rr = requests.get(url.split("?")[0], headers=UA, timeout=25)
                    if rr.status_code == 200 and len(rr.content) > 500:
                        fp = IMGDIR / f"{int(r['Código'])}.jpg"
                        fp.write_bytes(rr.content); local = fp.name
                except Exception:
                    pass
        fotos.append(local)
        time.sleep(0.05)
    df = df.copy()
    df.insert(1, "Nombre ES", nombres)
    if bajar_foto:
        df["Foto descargada"] = fotos
    return df

print("Enriqueciendo oportunidades + descargando fotos...")
op = enriquecer(op, True)
mono = enriquecer(mono, False)

cols = ["Código", "Nombre ES", "Categoría ES", "N° ofertas ML", "Costo 1688 CLP", "Precio alila CLP",
        "Precio mercado ML", "Margen vs alila CLP", "Margen vs alila %", "Margen vs 1688 CLP", "Margen vs 1688 %",
        "Score (margen/competencia)", "Link proveedor (1688)", "Link MercadoLibre",
        "N° fotos", "Foto principal", "Foto descargada"]
op_out = op[[c for c in cols if c in op.columns]]
mono_out = mono[[c for c in cols if c in mono.columns]]
pat = re.compile(r"ba[ñn]o|cocina|menaje|hogar|grifer|llave|ducha|organizador|mueble", re.I)
cerca = op_out[op_out["Categoría ES"].fillna("").str.contains(pat)]

dest = ROOT / "alila_oportunidades.xlsx"
with pd.ExcelWriter(dest, engine="xlsxwriter") as w:
    pd.DataFrame({"métrica": ["Oportunidades (2-5 ofertas, margen sano)", "Fotos descargadas",
                              "Cerca de tu línea", "Monopolio (1 oferta)", "Margen mediano %", "Margen mediano CLP"],
                  "valor": [len(op_out), int((op["Foto descargada"] != "").sum()), len(cerca), len(mono_out),
                            round(op_out["Margen vs alila %"].median(), 1), int(op_out["Margen vs alila CLP"].median())]}
                 ).to_excel(w, sheet_name="RESUMEN", index=False)
    op_out.head(50).to_excel(w, sheet_name="TOP_50", index=False)
    op_out.to_excel(w, sheet_name="OPORTUNIDADES", index=False)
    cerca.to_excel(w, sheet_name="CERCA_DE_TU_LINEA", index=False)
    mono_out.to_excel(w, sheet_name="MONOPOLIO_1_OFERTA", index=False)

print("=== LISTO ->", dest, "===")
print(f"Oportunidades: {len(op_out)} | fotos descargadas: {int((op['Foto descargada']!='').sum())} -> {IMGDIR.name}/")
print("\nTOP 15 con nombre limpio:")
print(op_out.head(15)[["Código", "Nombre ES", "N° ofertas ML", "Precio alila CLP", "Precio mercado ML", "Margen vs alila %"]].to_string(index=False))
