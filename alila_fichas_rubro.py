"""Ficha visual HTML de las ganadoras de MI RUBRO (mismo formato que el top10)."""
import pandas as pd, base64, requests
from pathlib import Path
ROOT = Path(r"C:\Users\dell\victtorino")
IMG = ROOT / "alila_oportunidades_fotos"; IMG.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
df = pd.read_excel(ROOT / "alila_oportunidades.xlsx", sheet_name="MI_RUBRO_GANADORAS")

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

cards = []
for i, (_, r) in enumerate(df.iterrows(), 1):
    cod = int(r["Código"]); foto = img64(foto_local(r))
    img_html = f'<img src="{foto}">' if foto else '<div class="noimg">sin foto</div>'
    l1688, lml = r.get("Link proveedor (1688)"), r.get("Link MercadoLibre")
    b1688 = f'<a href="{l1688}" target="_blank" class="b b1688">Comprar en 1688</a>' if isinstance(l1688, str) and l1688.startswith("http") else ""
    bml = f'<a href="{lml}" target="_blank" class="b bml">Ver en MercadoLibre</a>' if isinstance(lml, str) and lml.startswith("http") else ""
    sk = r.get("Stock alila"); sk = int(sk) if pd.notna(sk) else None
    if sk is None: stag = '<span class="tag">stock alila: s/d</span>'
    elif sk <= 0:  stag = '<span class="tag out">⚠ AGOTADO</span>'
    elif sk < 20:  stag = f'<span class="tag mid">stock alila: {sk} u (bajo)</span>'
    else:          stag = f'<span class="tag low">stock alila: {sk} u</span>'
    cards.append(f"""
    <div class="card"><div class="rank">#{i}</div>
      <div class="ph">{img_html}</div>
      <div class="info"><h2>{r['Nombre ES']}</h2>
        <div class="cat">{r.get('Categoría ES','')} · cód {cod}</div>
        <div class="grid">
          <div class="cell cost"><span>Te cuesta (alila)</span><b>{clp(r['Precio alila CLP'])}</b></div>
          <div class="cell cost1688"><span>Costo directo 1688</span><b>{clp(r['Costo 1688 CLP'])}</b></div>
          <div class="cell mkt"><span>Precio mercado ML</span><b>{clp(r['Precio mercado ML'])}</b></div>
          <div class="cell marg"><span>Margen (vs alila)</span><b>{clp(r['Margen vs alila CLP'])}<small> · {r['Margen vs alila %']}%</small></b></div>
        </div>
        <div class="meta">{stag}
          <span class="tag {'low' if r['N° ofertas ML']<=3 else 'mid'}">{int(r['N° ofertas ML'])} competidores en ML</span>
          <span class="tag alt">Margen 1688 directo: {r['Margen vs 1688 %']}%</span>
        </div>
        <div class="btns">{b1688}{bml}</div>
      </div></div>""")

html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Oportunidades de tu rubro — alila</title>
<style>*{{box-sizing:border-box}}body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#0f1115;color:#e7e9ee;margin:0;padding:28px}}
h1{{font-size:24px;margin:0 0 4px}}.sub{{color:#9aa3b2;margin:0 0 24px;font-size:14px}}
.card{{display:flex;gap:20px;background:#181b22;border:1px solid #262b36;border-radius:14px;padding:18px;margin-bottom:16px;position:relative;page-break-inside:avoid}}
.rank{{position:absolute;top:-10px;left:-10px;background:#16a34a;color:#fff;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;box-shadow:0 2px 8px #0008}}
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
<h1>Oportunidades de tu rubro (baño/cocina/hogar) — alila</h1>
<p class="sub">{len(df)} productos afines a tu línea con baja competencia + margen sano + stock disponible. CNY→CLP 130,9.</p>
{''.join(cards)}</body></html>"""
out = ROOT / "alila_fichas_rubro.html"
out.write_text(html, encoding="utf-8")
print("LISTO ->", out, "|", round(out.stat().st_size / 1024), "KB |", len(df), "fichas")
