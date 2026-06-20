"""
Agrega el stock real de alila (spkc.zl_kc) a la lista de oportunidades y a la ficha top10.
"""
import alila_app_client as A
import pandas as pd, json, base64, time
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
XLS = ROOT / "alila_oportunidades.xlsx"
IMG = ROOT / "alila_oportunidades_fotos"

A.auth()
def stock(hjh):
    try:
        r = A.coll_get("spkc", where={"hjh": int(hjh)}, limit=1)
        d = (r.get("data") or {}).get("data") or []
        if d:
            kc = d[0].get("zl_kc")
            # total comprado historico (proxy de rotacion)
            comp = sum(int(x.get("cgsl") or 0) for x in (d[0].get("cgj") or []) if isinstance(x, dict))
            return kc, comp
    except Exception:
        pass
    return None, None

# leer todas las hojas
sheets = pd.read_excel(XLS, sheet_name=None)
codigos = set()
for name, df in sheets.items():
    if "Código" in df.columns:
        codigos |= set(pd.to_numeric(df["Código"], errors="coerce").dropna().astype(int).tolist())
print(f"Consultando stock de {len(codigos)} productos...")

cache = {}
for k, c in enumerate(codigos, 1):
    if k % 50 == 0:
        A.auth(); print(f"  {k}/{len(codigos)}")
    cache[c] = stock(c)
    time.sleep(0.05)

# insertar columnas en cada hoja
for name, df in sheets.items():
    if "Código" not in df.columns:
        continue
    cod = pd.to_numeric(df["Código"], errors="coerce")
    df["Stock alila"] = cod.map(lambda c: cache.get(int(c), (None, None))[0] if pd.notna(c) else None)
    df["Comprado histórico"] = cod.map(lambda c: cache.get(int(c), (None, None))[1] if pd.notna(c) else None)
    # reubicar Stock alila despues de N° ofertas ML si existe
    if "N° ofertas ML" in df.columns:
        cols = list(df.columns)
        for mv in ["Comprado histórico", "Stock alila"]:
            cols.insert(cols.index("N° ofertas ML") + 1, cols.pop(cols.index(mv)))
        df = df[cols]
    sheets[name] = df

with pd.ExcelWriter(XLS, engine="xlsxwriter") as w:
    for name, df in sheets.items():
        df.to_excel(w, sheet_name=name, index=False)

con = sum(1 for v in cache.values() if v[0] is not None)
disp = sum(1 for v in cache.values() if (v[0] or 0) > 0)
print(f"Stock obtenido: {con}/{len(codigos)} | CON stock>0: {disp} | agotados: {con-disp}")

# ---- regenerar ficha top10 con stock ----
top = sheets["TOP_50"].head(10)
def img64(c):
    p = IMG / f"{int(c)}.jpg"
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() if p.exists() else ""
def clp(v):
    try: return f"${int(v):,}".replace(",", ".")
    except: return "—"

cards = []
for i, (_, r) in enumerate(top.iterrows(), 1):
    cod = r["Código"]; foto = img64(cod)
    img_html = f'<img src="{foto}">' if foto else '<div class="noimg">sin foto</div>'
    l1688 = r.get("Link proveedor (1688)"); lml = r.get("Link MercadoLibre")
    b1688 = f'<a href="{l1688}" target="_blank" class="b b1688">Comprar en 1688</a>' if isinstance(l1688, str) and l1688.startswith("http") else ""
    bml = f'<a href="{lml}" target="_blank" class="b bml">Ver en MercadoLibre</a>' if isinstance(lml, str) and lml.startswith("http") else ""
    sk = r.get("Stock alila")
    sk = int(sk) if pd.notna(sk) else None
    if sk is None: stag = '<span class="tag">stock alila: s/d</span>'
    elif sk <= 0:  stag = '<span class="tag out">⚠ AGOTADO en alila</span>'
    elif sk < 20:  stag = f'<span class="tag mid">stock alila: {sk} u (bajo)</span>'
    else:          stag = f'<span class="tag low">stock alila: {sk} u</span>'
    cards.append(f"""
    <div class="card"><div class="rank">#{i}</div>
      <div class="ph">{img_html}</div>
      <div class="info"><h2>{r['Nombre ES']}</h2>
        <div class="cat">{r.get('Categoría ES','')} · cód {int(cod)}</div>
        <div class="grid">
          <div class="cell cost"><span>Te cuesta (alila)</span><b>{clp(r['Precio alila CLP'])}</b></div>
          <div class="cell cost1688"><span>Costo directo 1688</span><b>{clp(r['Costo 1688 CLP'])}</b></div>
          <div class="cell mkt"><span>Precio mercado ML</span><b>{clp(r['Precio mercado ML'])}</b></div>
          <div class="cell marg"><span>Margen (vs alila)</span><b>{clp(r['Margen vs alila CLP'])}<small> · {r['Margen vs alila %']}%</small></b></div>
        </div>
        <div class="meta">
          {stag}
          <span class="tag {'low' if r['N° ofertas ML']<=3 else 'mid'}">{int(r['N° ofertas ML'])} competidores en ML</span>
          <span class="tag alt">Margen 1688 directo: {r['Margen vs 1688 %']}%</span>
        </div>
        <div class="btns">{b1688}{bml}</div>
      </div></div>""")

html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Top 10 Oportunidades alila</title>
<style>*{{box-sizing:border-box}}body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#0f1115;color:#e7e9ee;margin:0;padding:28px}}
h1{{font-size:24px;margin:0 0 4px}}.sub{{color:#9aa3b2;margin:0 0 24px;font-size:14px}}
.card{{display:flex;gap:20px;background:#181b22;border:1px solid #262b36;border-radius:14px;padding:18px;margin-bottom:16px;position:relative;page-break-inside:avoid}}
.rank{{position:absolute;top:-10px;left:-10px;background:#3b82f6;color:#fff;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;box-shadow:0 2px 8px #0008}}
.ph{{flex:0 0 190px;height:190px;background:#0c0e12;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden}}.ph img{{max-width:100%;max-height:100%;object-fit:contain}}.noimg{{color:#5a6273;font-size:13px}}
.info{{flex:1;min-width:0}}h2{{font-size:17px;margin:2px 0 2px;line-height:1.3}}.cat{{color:#8b93a3;font-size:12px;margin-bottom:14px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}}.cell{{background:#11141a;border:1px solid #232834;border-radius:9px;padding:10px}}
.cell span{{display:block;color:#8b93a3;font-size:11px;margin-bottom:3px}}.cell b{{font-size:17px}}.cell small{{font-size:12px;color:#9aa3b2;font-weight:500}}
.cost b{{color:#f0b86e}}.cost1688 b{{color:#c98bdb}}.mkt b{{color:#7fd1ff}}.marg b{{color:#5ee08a}}
.meta{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}}.tag{{font-size:11px;padding:4px 9px;border-radius:20px;background:#222733;color:#cfd5e0}}
.tag.low{{background:#0f2f1c;color:#6ee79e}}.tag.mid{{background:#33270f;color:#f2c879}}.tag.alt{{background:#1a2438;color:#9cc0ff}}.tag.out{{background:#3a1418;color:#ff8a8a;font-weight:700}}
.btns{{display:flex;gap:10px}}.b{{text-decoration:none;font-size:13px;font-weight:600;padding:9px 14px;border-radius:8px;color:#fff}}.b1688{{background:#ff6a00}}.bml{{background:#ffe600;color:#2d2d00}}
@media print{{body{{background:#fff;color:#000}}.card{{border-color:#ccc;background:#fff}}.cell{{background:#f6f7f9;border-color:#e2e5ea}}}}
</style></head><body>
<h1>Top 10 Oportunidades — alila</h1>
<p class="sub">Baja competencia (≤5 ofertas) + margen sano + stock del proveedor. CNY→CLP 130,9. ⚠ Verifica stock antes de prometer venta.</p>
{''.join(cards)}</body></html>"""
(ROOT / "alila_fichas_top10.html").write_text(html, encoding="utf-8")
print("Ficha regenerada con stock -> alila_fichas_top10.html")
print("\nStock del TOP 10:")
print(top[["Código", "Nombre ES", "Stock alila", "Comprado histórico", "Margen vs alila %"]].to_string(index=False))
