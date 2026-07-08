# -*- coding: utf-8 -*-
"""Agregar al portal los productos APROBADOS (curacion semanal, opcion B).
Recibe la lista de codigos elegidos (APROBADOS="6000028,6000031" o data/aprobados.txt)
e inserta SOLO esos (si aun no estan), ya INDEPENDIENTES de Alila:
 - fotos re-hospedadas en Cloudinary (via catalogo_utils.rehost_fotos)
 - descripcion limpia (sin chino/HTML/rastros)
 - linkML en NULL (sin rastro del proveedor)
Corre on-demand (boton "Run workflow")."""
import alila_app_client as A
import catalogo_utils as U
import psycopg2, re, os, uuid

DB_URL = os.environ["DATABASE_URL"]
MARGEN = (1.40, 1.35, 1.30)

# ---- codigos aprobados ----
raw = os.environ.get("APROBADOS", "").strip()
if not raw:
    from pathlib import Path
    f = Path(__file__).resolve().parent / "data" / "aprobados.txt"
    raw = f.read_text(encoding="utf-8") if f.exists() else ""
aprobados = {c for c in re.split(r'[\s,;]+', raw.strip()) if c}
if not aprobados:
    raise SystemExit("No hay codigos aprobados (APROBADOS vacio). Nada que agregar.")
print(f"Aprobados a agregar: {len(aprobados)} -> {sorted(aprobados)}")

# ---- helpers de precio/campos ----
def to_int(x):
    try: return int(float(str(x)))
    except: return None
def r100(v):
    return int(round(v/100.0)*100) if v else None
def clean(x):
    if x is None: return None
    s = str(x).strip()
    return s if s and s != "0" else None
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

# ---- insertar aprobados (independientes de Alila) ----
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
    sd = sk.get(cod) or {}
    nombre = U.limpiar_nombre(d.get("mc"))
    costo = costo_alila(d)
    if not nombre:
        saltados.append((cod, "sin nombre util")); continue
    if not costo:
        saltados.append((cod, "sin costo")); continue
    stock = to_int(sd.get("zl_kc")) or 0
    fotos_cloud = U.rehost_fotos(cod, d.get("tp") or [])   # -> URLs Cloudinary propias
    foto1 = fotos_cloud[0] if fotos_cloud else None
    desc = U.limpiar_desc(d.get("sm"))
    cur.execute(
        'INSERT INTO "Producto" (id,"codigoAlila",nombre,categoria,costo,"precioT1","precioT2","precioT3",'
        '"unidCaja","fotoUrl",fotos,descripcion,dimensiones,embalaje,keywords,"nArticulo",'
        '"codigoProveedor","linkML",activo,stock) '
        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        ("c" + uuid.uuid4().hex[:24], cod, nombre, clean_cat(d.get("x_lm")), costo,
         r100(costo*MARGEN[0]), r100(costo*MARGEN[1]), r100(costo*MARGEN[2]),
         to_int(d.get("zxs")), foto1, fotos_cloud, desc,
         clean(d.get("sp_cc")), clean(d.get("bz_ss")), clean(d.get("ss_cy")), clean(d.get("hh")),
         clean(d.get("gys_hjh")), None, stock > 0, stock))
    con.commit()
    en_portal.add(cod); agregados += 1
    print(f"  + {cod}  {nombre[:45]}  T1 ${r100(costo*MARGEN[0])}  fotos:{len(fotos_cloud)}")

cur.close(); con.close()
print(f"\nAGREGADOS: {agregados}")
if saltados:
    print("SALTADOS:")
    for cod, motivo in saltados:
        print(f"  - {cod}: {motivo}")
