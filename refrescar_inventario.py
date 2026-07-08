# -*- coding: utf-8 -*-
"""Refresco diario de inventario del Portal Mayorista.
Baja stock + info desde AlilaTop (solo lectura) y actualiza la base Neon.
Regla: producto SIN stock => activo=False.

IMPORTANTE (2026-07-08): el catalogo ahora es INDEPENDIENTE de Alila (fotos en
Cloudinary + descripciones limpias, via migrar_catalogo.py / agregar_aprobados.py).
Por eso el refresco diario YA NO toca fotos, fotoUrl ni descripcion (no las pisa),
y deja linkML en NULL (sin rastros del proveedor). Solo actualiza lo que cambia:
STOCK, ACTIVO y PRECIOS. El alta automatica quedo DESACTIVADA: los productos
nuevos entran por curacion semanal (candidatos_semana.py + agregar_aprobados.py).

Salvaguardas: (1) nunca baja stock bajo lo RESERVADO; (2) no desactiva productos
con pedidos en curso; (3) si el scrape viene vacio/parcial, aborta; (4) respaldo CSV."""
import alila_app_client as A
import psycopg2, json, re, uuid, csv, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    ENV = (ROOT / "portal-mayorista" / ".env").read_text(encoding="utf-8")
    DB_URL = re.search(r'DATABASE_URL="([^"]+)"', ENV).group(1)

# Alta automatica diaria DESACTIVADA (ahora se usa curacion semanal). Poner True para reactivar.
AUTO_ALTA_DIARIA = False
PISO_DEMANDA = 570

def to_int(x):
    try: return int(float(str(x)))
    except: return None

def r100(v):
    return int(round(v/100.0)*100) if v else None

MARGEN = (1.40, 1.35, 1.30)

def costo_alila(d):
    for x in (d.get("pf") or []):
        if isinstance(x, dict) and x.get("xsj"):
            return to_int(x.get("xsj"))
    return None

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

# 1a) info rica (hjxq)
A.auth(); alila = {}; skip = 0; lim = 100
while True:
    if skip and skip % 1000 == 0: A.auth()
    r = A.coll_get("hjxq", where=None, skip=skip, limit=lim)
    data = (r.get("data") or {}).get("data") or []
    if not data: break
    for d in data:
        cod = str(d.get("hjh") or "").strip()
        if cod: alila[cod] = d
    skip += lim
    if len(data) < lim: break
print(f"Alila hjxq: {len(alila)} productos")

# 1b) STOCK REAL + demanda (spkc)
sk = {}; skip = 0
while True:
    if skip and skip % 1000 == 0: A.auth()
    r = A.coll_get("spkc", where=None, skip=skip, limit=lim)
    data = (r.get("data") or {}).get("data") or []
    if not data: break
    for d in data:
        cod = str(d.get("hjh") or "").strip()
        if cod: sk[cod] = d
    skip += lim
    if len(data) < lim: break
print(f"Alila spkc (stock): {len(sk)} productos")

MIN_SCRAPE = 500
if len(alila) < MIN_SCRAPE or len(sk) < MIN_SCRAPE:
    raise SystemExit(f"ABORTADO: scrape parcial (hjxq={len(alila)}, spkc={len(sk)} < {MIN_SCRAPE}). No se toca la base.")

# 2) actualizar productos del portal
con = psycopg2.connect(DB_URL); cur = con.cursor()

# Respaldo reversible
cur.execute('SELECT id, "codigoAlila", stock, reservado, "precioT1", "precioT2", "precioT3", activo FROM "Producto"')
filas_bak = cur.fetchall()
bak = ROOT / "data" / "backups"; bak.mkdir(parents=True, exist_ok=True)
bak_file = bak / f"productos_{datetime.now():%Y%m%d_%H%M%S}.csv"
with open(bak_file, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id","codigoAlila","stock","reservado","precioT1","precioT2","precioT3","activo"]); w.writerows(filas_bak)
print(f"Respaldo: {bak_file.name} ({len(filas_bak)} filas)")

# Productos con pedidos en curso: NO desactivar
cur.execute('SELECT DISTINCT pi."productoId" FROM "PedidoItem" pi JOIN "Pedido" p ON p.id=pi."pedidoId" WHERE p.estado IN (%s,%s)', ("validado","oc_generada"))
en_curso = {r[0] for r in cur.fetchall()}

cur.execute('SELECT id, reservado FROM "Producto"')
reservado_de = {pid: r for pid, r in cur.fetchall()}

prods = [(pid, cod) for pid, cod, *_ in filas_bak]
en_portal = {cod for _, cod in prods}
upd = act = inact = sin = bajo_reserva = 0
for pid, cod in prods:
    d = alila.get(cod)
    if not d:
        sin += 1
        if pid not in en_curso:
            cur.execute('UPDATE "Producto" SET activo=false WHERE id=%s', (pid,))
            inact += 1
        continue
    sd = sk.get(cod) or {}
    stock = to_int(sd.get("zl_kc")) or 0
    res = reservado_de.get(pid, 0)
    if stock < res:
        bajo_reserva += 1
        stock = res
    activo = stock > 0 or pid in en_curso
    # reprice desde el costo real de AlilaTop (pf)
    costo = costo_alila(d)
    t1 = r100(costo*MARGEN[0]) if costo else None
    t2 = r100(costo*MARGEN[1]) if costo else None
    t3 = r100(costo*MARGEN[2]) if costo else None
    nombre = sin_chino(d.get("mc"))
    cat = clean_cat(d.get("x_lm"))
    # NO se tocan fotos/fotoUrl/descripcion (gestionadas por Cloudinary) ni se
    # re-agrega linkML (se deja NULL). Solo stock/activo/precios/meta basica.
    cur.execute(
        'UPDATE "Producto" SET stock=%s, activo=%s,'
        ' nombre=COALESCE(%s,nombre), categoria=COALESCE(%s,categoria),'
        ' "dimensiones"=%s, "embalaje"=%s, "keywords"=%s, "nArticulo"=%s,'
        ' "codigoProveedor"=%s, "unidCaja"=COALESCE(%s,"unidCaja"), "linkML"=NULL,'
        ' costo=COALESCE(%s,costo), "precioT1"=COALESCE(%s,"precioT1"),'
        ' "precioT2"=COALESCE(%s,"precioT2"), "precioT3"=COALESCE(%s,"precioT3") WHERE id=%s',
        (stock, activo, nombre, cat, clean(d.get("sp_cc")),
         clean(d.get("bz_ss")), clean(d.get("ss_cy")), clean(d.get("hh")),
         clean(d.get("gys_hjh")), to_int(d.get("zxs")),
         costo, t1, t2, t3, pid))
    upd += 1
    if activo: act += 1
    else: inact += 1

# 3) alta automatica (DESACTIVADA por defecto -> curacion semanal la reemplaza)
nuevos = 0
for cod, d in (alila.items() if AUTO_ALTA_DIARIA else []):
    if cod in en_portal:
        continue
    sd = sk.get(cod) or {}
    dem = to_int(sd.get("zxl")) or 0
    stock = to_int(sd.get("zl_kc")) or 0
    costo = costo_alila(d)
    if not (stock > 0 and dem >= PISO_DEMANDA and costo):
        continue
    nombre = sin_chino(d.get("mc"))
    if not nombre:
        continue
    fotos = d.get("tp") or []
    cur.execute(
        'INSERT INTO "Producto" (id,"codigoAlila",nombre,categoria,costo,"precioT1","precioT2","precioT3",'
        '"unidCaja","fotoUrl",fotos,descripcion,dimensiones,embalaje,keywords,"nArticulo",'
        '"codigoProveedor","linkML",activo,stock) '
        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        ("c" + uuid.uuid4().hex[:24], cod, nombre, clean_cat(d.get("x_lm")), costo,
         r100(costo*MARGEN[0]), r100(costo*MARGEN[1]), r100(costo*MARGEN[2]),
         to_int(d.get("zxs")), (fotos[0] if fotos else None), fotos, sin_chino(d.get("sm")),
         clean(d.get("sp_cc")), clean(d.get("bz_ss")), clean(d.get("ss_cy")), clean(d.get("hh")),
         clean(d.get("gys_hjh")), None, True, stock))
    en_portal.add(cod)
    nuevos += 1
    act += 1

con.commit()
print(f"Portal: {len(prods)} productos | actualizados {upd} | sin match en Alila {sin}")
print(f"ALTAS nuevas: {nuevos} (auto-alta {'ON' if AUTO_ALTA_DIARIA else 'OFF: usar curacion semanal'})")
print(f"ACTIVOS: {act} | inactivos: {inact}")
if bajo_reserva:
    print(f"OJO: {bajo_reserva} productos con stock AlilaTop < reservado (se mantuvo el reservado)")
cur.close(); con.close()
