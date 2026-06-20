"""Lista COMPLETA de complementarios baño/cocina (139), con o sin precio de mercado,
priorizando los que tienen stock. + ficha ampliada."""
import alila_app_client as A
import pandas as pd, re, json, time, base64, requests
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
IMG = ROOT / "alila_oportunidades_fotos"; IMG.mkdir(exist_ok=True)
CNY_CLP = 130.9
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
XLS = ROOT / "alila_oportunidades.xlsx"

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
al["Precio mercado ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("precio_min") if i else None)
al["N° ofertas ML"] = al["mkt_id"].map(lambda i: (cache.get(i) or {}).get("n_ofertas") if i else None)
al["Costo 1688 CLP"] = (pd.to_numeric(al["Costo compra"], errors="coerce") * CNY_CLP).round()
al["Precio alila CLP"] = pd.to_numeric(al["Precio (1u/menor cant.)"], errors="coerce")
mkt = pd.to_numeric(al["Precio mercado ML"], errors="coerce")
al["Margen vs alila CLP"] = (mkt - al["Precio alila CLP"]).round()
al["Margen vs alila %"] = ((al["Margen vs alila CLP"] / mkt) * 100).round(1)

cat = al["Categoría ES"].fillna("")
comp = al[(al["Estado"] == "上线销售") &
          cat.str.contains(r"Cocina y Menaje|Hogar y Muebles>Baños|Mobiliario para Baños|Mobiliario para Cocinas")].copy()
comp["Nombre ES"] = comp.apply(lambda r: slug(r["Link MercadoLibre"]) or r.get("Nombre (EN)") or "(revisar foto)", axis=1)

A.auth()
def stock(hjh):
    try:
        d = (A.coll_get("spkc", where={"hjh": int(hjh)}, limit=1).get("data") or {}).get("data") or []
        return d[0].get("zl_kc") if d else None
    except Exception: return None
sk = []
for k, c in enumerate(comp["Código"], 1):
    if k % 50 == 0: A.auth()
    sk.append(stock(c)); time.sleep(0.05)
comp["Stock alila"] = sk
comp["Precio venta (tú defines)"] = comp["Precio mercado ML"].where(comp["Precio mercado ML"].notna(), "")

cols = ["Código", "Nombre ES", "Categoría ES", "Stock alila", "N° ofertas ML",
        "Costo 1688 CLP", "Precio alila CLP", "Precio mercado ML", "Margen vs alila CLP", "Margen vs alila %",
        "Link proveedor (1688)", "Link MercadoLibre", "N° fotos", "Foto principal"]
comp = comp[[c for c in cols if c in comp.columns]]
# orden: con stock primero, luego con precio de mercado, luego margen
comp["_o1"] = (comp["Stock alila"].fillna(-1) > 0).astype(int)
comp["_o2"] = comp["Precio mercado ML"].notna().astype(int)
comp = comp.sort_values(["_o1", "_o2", "Margen vs alila CLP"], ascending=[False, False, False]).drop(columns=["_o1", "_o2"])

sheets = pd.read_excel(XLS, sheet_name=None)
sheets["COMPLEMENTARIOS_FULL"] = comp
with pd.ExcelWriter(XLS, engine="xlsxwriter") as w:
    for n, d in sheets.items(): d.to_excel(w, sheet_name=n[:31], index=False)

# ficha: con stock>0, hasta 18 (priorizando los que tienen margen calculado, luego sin precio)
def foto_local(r):
    cod = int(r["Código"]); p = IMG / f"{cod}.jpg"
    if not p.exists():
        u = r.get("Foto principal")
        if isinstance(u, str) and u.startswith("http"):
            try:
                rr = requests.get(u.split("?")[0], headers=UA, timeout=25)
                if rr.status_code == 200 and len(rr.content) > 500: p.write_bytes(rr.content)
            except Exception: pass
    return p
def img64(p): return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() if p.exists() else ""
def clp(v):
    try: return f"${int(v):,}".replace(",", ".")
    except: return "—"

ficha = comp[comp["Stock alila"].fillna(0) > 0].head(18)
cards = []
for i, (_, r) in enumerate(ficha.iterrows(), 1):
    cod = int(r["Código"]); foto = img64(foto_local(r))
    img_html = f'<img src="{foto}">' if foto else '<div class="noimg">sin foto</div>'
    l1688, lml = r.get("Link proveedor (1688)"), r.get("Link MercadoLibre")
    b1688 = f'<a href="{l1688}" target="_blank" class="b b1688">Comprar en 1688</a>' if isinstance(l1688, str) and l1688.startswith("http") else ""
    bml = f'<a href="{lml}" target="_blank" class="b bml">Ver en ML</a>' if isinstance(lml, str) and lml.startswith("http") else ""
    s = r.get("Stock alila"); s = int(s) if pd.notna(s) else None
    stag = (f'<span class="tag low">stock: {s} u</span>' if s and s >= 20 else
            f'<span class="tag mid">stock: {s} u</span>' if s else '<span class="tag">s/d</span>')
    if pd.notna(r["Precio mercado ML"]):
        mblock = f'<div class="cell mkt"><span>Precio mercado ML</span><b>{clp(r["Precio mercado ML"])}</b></div><div class="cell marg"><span>Margen vs alila</span><b>{clp(r["Margen vs alila CLP"])}<small> · {r["Margen vs alila %"]}%</small></b></div>'
        comptag = f'<span class="tag {"low" if r["N° ofertas ML"]<=3 else "mid"}">{int(r["N° ofertas ML"])} competidores</span>' if pd.notna(r["N° ofertas ML"]) else ""
    else:
        mblock = '<div class="cell mkt"><span>Precio mercado ML</span><b style="color:#8b93a3">tú lo defines</b></div><div class="cell marg"><span>Margen</span><b style="color:#8b93a3">—</b></div>'
        comptag = '<span class="tag">sin referencia ML</span>'
    cards.append(f"""
    <div class="card"><div class="rank">#{i}</div><div class="ph">{img_html}</div>
      <div class="info"><h2>{r['Nombre ES']}</h2><div class="cat">{r.get('Categoría ES','')} · cód {cod}</div>
        <div class="grid">
          <div class="cell cost"><span>Te cuesta (alila)</span><b>{clp(r['Precio alila CLP'])}</b></div>
          <div class="cell cost1688"><span>Costo directo 1688</span><b>{clp(r['Costo 1688 CLP'])}</b></div>
          {mblock}
        </div>
        <div class="meta">{stag}{comptag}</div>
        <div class="btns">{b1688}{bml}</div></div></div>""")

html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Complementarios baño/cocina (completo) — alila</title>
<style>*{{box-sizing:border-box}}body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#0f1115;color:#e7e9ee;margin:0;padding:28px}}
h1{{font-size:24px;margin:0 0 4px}}.sub{{color:#9aa3b2;margin:0 0 24px;font-size:14px}}
.card{{display:flex;gap:20px;background:#181b22;border:1px solid #262b36;border-radius:14px;padding:18px;margin-bottom:16px;position:relative;page-break-inside:avoid}}
.rank{{position:absolute;top:-10px;left:-10px;background:#0891b2;color:#fff;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;box-shadow:0 2px 8px #0008}}
.ph{{flex:0 0 170px;height:170px;background:#0c0e12;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden}}.ph img{{max-width:100%;max-height:100%;object-fit:contain}}.noimg{{color:#5a6273;font-size:13px}}
.info{{flex:1;min-width:0}}h2{{font-size:16px;margin:2px 0 2px;line-height:1.3}}.cat{{color:#8b93a3;font-size:12px;margin-bottom:14px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}}.cell{{background:#11141a;border:1px solid #232834;border-radius:9px;padding:10px}}
.cell span{{display:block;color:#8b93a3;font-size:11px;margin-bottom:3px}}.cell b{{font-size:16px}}.cell small{{font-size:12px;color:#9aa3b2;font-weight:500}}
.cost b{{color:#f0b86e}}.cost1688 b{{color:#c98bdb}}.mkt b{{color:#7fd1ff}}.marg b{{color:#5ee08a}}
.meta{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}}.tag{{font-size:11px;padding:4px 9px;border-radius:20px;background:#222733;color:#cfd5e0}}
.tag.low{{background:#0f2f1c;color:#6ee79e}}.tag.mid{{background:#33270f;color:#f2c879}}
.btns{{display:flex;gap:10px}}.b{{text-decoration:none;font-size:13px;font-weight:600;padding:9px 14px;border-radius:8px;color:#fff}}.b1688{{background:#ff6a00}}.bml{{background:#ffe600;color:#2d2d00}}
@media print{{body{{background:#fff;color:#000}}.card{{border-color:#ccc;background:#fff}}.cell{{background:#f6f7f9;border-color:#e2e5ea}}}}
</style></head><body>
<h1>Complementarios de baño y cocina — catálogo completo</h1>
<p class="sub">{len(ficha)} con stock (de {len(comp)} totales). Donde hay referencia ML se muestra margen; donde no, defines tú el precio. Costo a precio alila y a 1688 directo. CNY→CLP 130,9.</p>
{''.join(cards)}</body></html>"""
out = ROOT / "alila_fichas_complementarios.html"
out.write_text(html, encoding="utf-8")
print(f"Complementarios totales: {len(comp)} | con stock>0: {int((comp['Stock alila'].fillna(0)>0).sum())} | con precio mercado: {int(comp['Precio mercado ML'].notna().sum())}")
print(f"Ficha ampliada: {out.name} ({round(out.stat().st_size/1024)} KB, {len(ficha)} fichas con stock)")
print("\nCon stock, primeros 20:")
print(comp[comp['Stock alila'].fillna(0)>0].head(20)[["Nombre ES","Categoría ES","Stock alila","Precio alila CLP","Precio mercado ML","Margen vs alila %"]].to_string(index=False))
