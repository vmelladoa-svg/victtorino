# -*- coding: utf-8 -*-
"""Agregar al portal los productos APROBADOS (opcion B: curacion manual).
Recibe la lista de codigos que Victor eligio (variable APROBADOS="6000028,6000031"
o el archivo data/aprobados.txt). Inserta SOLO esos (si aun no estan en el portal),
con el MISMO margen y limpieza que refrescar_inventario.py. Corre on-demand
(boton "Run workflow" en GitHub Actions)."""
import alila_app_client as A
import psycopg2, re, os, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_URL = os.environ["DATABASE_URL"]
MARGEN = (1.40, 1.35, 1.30)

# ---- lista de codigos aprobados (variable de entorno o archivo) ----
raw = os.environ.get("APROBADOS", "").strip()
if not raw:
    f = ROOT / "data" / "aprobados.txt"
    raw = f.read_text(encoding="utf-8") if f.exists() else ""
aprobados = {c for c in re.split(r'[\s,;]+', raw.strip()) if c}
if not aprobados:
    raise SystemExit("No hay codigos aprobados (APROBADOS vacio). Nada que agregar.")
print(f"Aprobados a agregar: {len(aprobados)} -> {sorted(aprobados)}")

# ---- helpers (identicos a refrescar_inventario.py) ----
def to_int(x):
    try: return int(float(str(x)))
    except: return None
def r100(v):
    return int(round(v/100.0)*100) if v else None
def clean(x):
    if x is None: return None
    s = str(x).strip()
    return s if s and s != "0" else None
_CJK = re.compile(r'[　-〿㐀-䶿一-鿿豈-﫿＀-￯]+')
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
def campos_ricos(d, sd):
    stock = to_int(sd.get("zl_kc")) or 0
    costo = costo_alila(d)
    return {
        "stock": stock, "activo": stock > 0,
        "fotos": d.get("tp") or [], "foto1": (d.get("tp") or [None])[0],
        "nombre": sin_chino(d.get("mc")), "cat": clean_cat(d.get("x_lm")),
        "desc": sin_chino(d.get("sm")), "dim": clean(d.get("sp_cc")),
        "emb": clean(d.get("bz_ss")), "kw": clean(d.get("ss_cy")), "narti": clean(d.get("hh")),
        "codprov": clean(d.get("gys_hjh")), "unidcaja": to_int(d.get("zxs")), "linkml": clean(d.get("ml_lj")),
        "costo": costo,
        "t1": r100(costo*MARGEN[0]) if costo else None,
        "t2": r100(costo*MARGEN[1]) if costo else None,
        "t3": r100(costo*MARGEN[2]) if costo else None,
    }

def bajar(coll):
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

# ---- bajar Alila ----
A.auth()
alila = bajar("hjxq"); sk = bajar("spkc")
print(f"Alila: hjxq={len(alila)} spkc={len(sk)}")
if len(alila) < 500:
    raise SystemExit("ABORTADO: scrape parcial, no se agrega nada.")

# ---- insertar aprobados ----
con = psycopg2.connect(DB_URL); cur = con.cursor()
cur.execute('SELECT "codigoAlila" FROM "Producto"')
en_portal = {r[0] for r in cur.fetchall()}

agregados = 0; saltados = []
for cod in aprobados:
    if cod in en_portal:
        saltados.append((cod, "ya en portal")); continue
    d = alila.get(cod)
    if not d:
        saltados.append((cod, "no esta en Alila")); continue
    c = campos_ricos(d, sk.get(cod) or {})
    if not c["nombre"]:
        saltados.append((cod, "sin nombre util")); continue
    if not c["costo"]:
        saltados.append((cod, "sin costo")); continue
    cur.execute(
        'INSERT INTO "Producto" (id,"codigoAlila",nombre,categoria,costo,"precioT1","precioT2","precioT3",'
        '"unidCaja","fotoUrl",fotos,descripcion,dimensiones,embalaje,keywords,"nArticulo",'
        '"codigoProveedor","linkML",activo,stock) '
        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        ("c" + uuid.uuid4().hex[:24], cod, c["nombre"], c["cat"], c["costo"], c["t1"], c["t2"], c["t3"],
         c["unidcaja"], c["foto1"], c["fotos"], c["desc"], c["dim"], c["emb"], c["kw"], c["narti"],
         c["codprov"], c["linkml"], c["activo"], c["stock"]))
    en_portal.add(cod); agregados += 1
    print(f"  + {cod}  {(c['nombre'] or '')[:50]}  (T1 ${c['t1']})")

con.commit(); cur.close(); con.close()
print(f"\nAGREGADOS: {agregados}")
if saltados:
    print("SALTADOS:")
    for cod, motivo in saltados:
        print(f"  - {cod}: {motivo}")
