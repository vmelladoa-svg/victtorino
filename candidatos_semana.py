# -*- coding: utf-8 -*-
"""Candidatos semanales: productos de AlilaTop que NO estan en el portal.
SOLO LECTURA (no inserta nada). Arma la lista para que Victor la revise en una
pagina visual y elija cuales agregar. Corre semanal en GitHub Actions:
 - deja data/candidatos.json en el repo (fuente de la pagina de revision)
 - manda un WhatsApp con el resumen (CallMeBot)
Reusa la misma API (alila_app_client) y limpieza que refrescar_inventario.py."""
import alila_app_client as A
import psycopg2, json, re, os, urllib.parse, urllib.request
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB_URL = os.environ["DATABASE_URL"]           # secreto en GitHub Actions
TOP_N = int(os.environ.get("CANDIDATOS_TOP", "60"))  # cap para revision manejable
MARGEN = (1.40, 1.35, 1.30)                   # mismo margen del portal

# ---- helpers (identicos a refrescar_inventario.py, para consistencia) ----
def to_int(x):
    try: return int(float(str(x)))
    except: return None
def r100(v):
    return int(round(v/100.0)*100) if v else None
def clean(x):
    if x is None: return None
    s = str(x).strip()
    return s if s and s != "0" else None
_CJK = re.compile(r'[　-〿㐀-䶿一-鿿豈-﫿＀-￯]+')
def sin_chino(x):
    if x is None: return None
    s = _CJK.sub('', str(x))
    s = re.sub(r'\s{2,}', ' ', s).strip(' ,-·|/').strip()
    return s or None
def clean_cat(x):
    s = clean(x)
    if not s: return None
    s = s.replace(">[object Object]", "").replace("[object Object]", "")
    s = re.sub(r'(^|>)nstrumentos', r'\1Instrumentos', s)
    return s.rstrip(">").strip() or None
def costo_alila(d):
    for x in (d.get("pf") or []):
        if isinstance(x, dict) and x.get("xsj"):
            return to_int(x.get("xsj"))
    return None

def bajar(coll):
    """Baja una coleccion completa de Alila -> mapa por codigo (hjh)."""
    out = {}; skip = 0; lim = 100
    while True:
        if skip and skip % 1000 == 0: A.auth()
        r = A.coll_get(coll, where=None, skip=skip, limit=lim)
        data = (r.get("data") or {}).get("data") or []
        if not data: break
        for d in data:
            cod = str(d.get("hjh") or "").strip()
            if cod: out[cod] = d
        skip += lim
        if len(data) < lim: break
    return out

# ---- 1) bajar info (hjxq) + stock/demanda (spkc) ----
A.auth()
alila = bajar("hjxq")
sk = bajar("spkc")
print(f"Alila: hjxq={len(alila)}  spkc={len(sk)}")
MIN_SCRAPE = 500
if len(alila) < MIN_SCRAPE or len(sk) < MIN_SCRAPE:
    raise SystemExit(f"ABORTADO: scrape parcial (hjxq={len(alila)}, spkc={len(sk)}).")

# ---- 2) codigos ya presentes en el portal ----
con = psycopg2.connect(DB_URL); cur = con.cursor()
cur.execute('SELECT "codigoAlila" FROM "Producto"')
en_portal = {r[0] for r in cur.fetchall()}
cur.close(); con.close()
print(f"Portal: {len(en_portal)} productos existentes")

# ---- 3) candidatos: en Alila, NO en portal, con stock>0, costo y nombre ----
cands = []
for cod, d in alila.items():
    if cod in en_portal:
        continue
    sd = sk.get(cod) or {}
    stock = to_int(sd.get("zl_kc")) or 0
    dem = to_int(sd.get("zxl")) or 0
    costo = costo_alila(d)
    if not (stock > 0 and costo):
        continue
    nombre = sin_chino(d.get("mc"))
    if not nombre:
        continue
    fotos = d.get("tp") or []
    cands.append({
        "codigo": cod,
        "nombre": nombre,
        "categoria": clean_cat(d.get("x_lm")),
        "costo": costo,
        "precioT1": r100(costo * MARGEN[0]),
        "demanda": dem,
        "stock": stock,
        "foto": fotos[0] if fotos else None,
        "descripcion": sin_chino(d.get("sm")),
    })

cands.sort(key=lambda c: c["demanda"], reverse=True)   # mas vendidos primero
total = len(cands)
cands = cands[:TOP_N]

# ---- 4) guardar json (fuente de la pagina de revision) ----
out = {
    "generado": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_candidatos": total,
    "mostrados": len(cands),
    "candidatos": cands,
}
data_dir = ROOT / "data"; data_dir.mkdir(exist_ok=True)
(data_dir / "candidatos.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Candidatos NUEVOS: {total} (guardados top {len(cands)} por demanda)")

# ---- 5) aviso por WhatsApp ----
phone = os.environ.get("CALLMEBOT_PHONE"); apikey = os.environ.get("CALLMEBOT_APIKEY")
if phone and apikey and total:
    msg = (f"🆕 Comercial Solutions: {total} productos NUEVOS de Alila para revisar esta semana "
           f"(top {len(cands)} por demanda). Revisa la pagina y elige cuales agregar.")
    url = "https://api.callmebot.com/whatsapp.php?phone=%s&text=%s&apikey=%s" % (
        phone, urllib.parse.quote(msg), apikey)
    try:
        urllib.request.urlopen(url, timeout=30); print("WhatsApp enviado.")
    except Exception as e:
        print("WhatsApp fallo:", e)
elif not total:
    print("Sin candidatos nuevos esta semana; no se envia WhatsApp.")
