# -*- coding: utf-8 -*-
"""Refresco diario de inventario del Portal Mayorista.
Baja stock + info rica desde AlilaTop (backend uniCloud, solo lectura) y actualiza
la base Neon del portal. Regla: producto SIN stock => activo=False (no se ofrece).
Pensado para correr por Tarea Programada de Windows (diario).

REPRICEA a diario: recalcula los tramos T1/T2/T3 desde el costo real de AlilaTop
(primer tramo de pf) por los margenes 40/35/30%. Si ajustas un precio a mano en el
portal, este refresco lo revierte al dia siguiente (es el comportamiento buscado).

Salvaguardas: (1) nunca baja stock por debajo de lo ya RESERVADO (respeta pedidos
validados); (2) no desactiva productos con pedidos en curso; (3) si el scrape de
AlilaTop viene vacio/parcial, aborta sin apagar el catalogo; (4) deja un respaldo
CSV reversible antes del UPDATE masivo."""
import alila_app_client as A
import psycopg2, json, re, uuid, csv, os
from traducir_cn import traducir
from pathlib import Path
from datetime import datetime

# ROOT = carpeta del script (funciona en el PC y en GitHub Actions).
ROOT = Path(__file__).resolve().parent
# DATABASE_URL: variable de entorno (nube) o, si no, el .env local (PC).
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    ENV = (ROOT / "portal-mayorista" / ".env").read_text(encoding="utf-8")
    DB_URL = re.search(r'DATABASE_URL="([^"]+)"', ENV).group(1)

# alta automatica de productos nuevos: mismo bar que los 150 originales
# (stock>0 + demanda historica zxl>=PISO + costo valido). Hoy => 6 candidatos.
PISO_DEMANDA = 570

def to_int(x):
    try: return int(float(str(x)))
    except: return None

def r100(v):
    return int(round(v/100.0)*100) if v else None

# margen mayorista sobre el costo real de AlilaTop (pf): 40/35/30% por tramo (despacho aparte)
MARGEN = (1.40, 1.35, 1.30)

def costo_alila(d):
    # costo real = primer tramo de pf (precio AlilaTop a la cantidad minima)
    for x in (d.get("pf") or []):
        if isinstance(x, dict) and x.get("xsj"):
            return to_int(x.get("xsj"))
    return None

def clean(x):
    if x is None: return None
    s = str(x).strip()
    return s if s and s != "0" else None

# quitar caracteres chinos (CJK) y fullwidth, limpiar espacios
_CJK = re.compile(r'[　-〿㐀-䶿一-鿿豈-﫿＀-￯]+')
def sin_chino(x):
    if x is None: return None
    s = _CJK.sub('', str(x))
    s = re.sub(r'\s{2,}', ' ', s).strip(' ,-·|/').strip()
    return s or None

def clean_cat(x):
    s = clean(x)
    if not s: return None
    # arreglar subcategoria rota y typo de Instrumentos
    s = s.replace(">[object Object]", "").replace("[object Object]", "")
    s = re.sub(r'(^|>)nstrumentos', r'\1Instrumentos', s)
    return s.rstrip(">").strip() or None

# 1a) bajar info rica (hjxq) -> mapa por codigo
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

# 1b) bajar STOCK REAL + demanda (spkc) -> mapa por codigo
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

# GUARD: si el scrape vino vacio o sospechosamente parcial, abortar SIN tocar la
# base. Evita apagar medio catalogo por un timeout o una auth caida a mitad.
MIN_SCRAPE = 500  # el catalogo real de AlilaTop son miles; <500 = scrape roto
if len(alila) < MIN_SCRAPE or len(sk) < MIN_SCRAPE:
    raise SystemExit(f"ABORTADO: scrape parcial (hjxq={len(alila)}, spkc={len(sk)} < {MIN_SCRAPE}). No se toca la base.")

# helpers de campos ricos comunes a update e insert
def campos_ricos(d, sd):
    stock = to_int(sd.get("zl_kc")) or 0
    costo = costo_alila(d)
    return {
        "stock": stock, "activo": stock > 0,
        "fotos": d.get("tp") or [], "foto1": (d.get("tp") or [None])[0],
        "nombre": sin_chino(d.get("mc")), "cat": clean_cat(d.get("x_lm")),
        "desc": sin_chino(d.get("sm")), "dim": traducir(clean(d.get("sp_cc"))),
        "emb": traducir(clean(d.get("bz_ss"))), "kw": clean(d.get("ss_cy")), "narti": clean(d.get("hh")),
        "codprov": clean(d.get("gys_hjh")), "unidcaja": to_int(d.get("zxs")), "linkml": clean(d.get("ml_lj")),
        "costo": costo,
        "t1": r100(costo*MARGEN[0]) if costo else None,
        "t2": r100(costo*MARGEN[1]) if costo else None,
        "t3": r100(costo*MARGEN[2]) if costo else None,
    }

# 2) actualizar productos del portal
con = psycopg2.connect(DB_URL); cur = con.cursor()

# Respaldo reversible: volcar estado actual antes del UPDATE masivo.
cur.execute('SELECT id, "codigoAlila", stock, reservado, "precioT1", "precioT2", "precioT3", activo FROM "Producto"')
filas_bak = cur.fetchall()
bak = ROOT / "data" / "backups"; bak.mkdir(parents=True, exist_ok=True)
bak_file = bak / f"productos_{datetime.now():%Y%m%d_%H%M%S}.csv"
with open(bak_file, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id","codigoAlila","stock","reservado","precioT1","precioT2","precioT3","activo"]); w.writerows(filas_bak)
print(f"Respaldo: {bak_file.name} ({len(filas_bak)} filas)")

# Productos con pedidos en curso (validado / oc_generada): NO desactivar aunque
# AlilaTop los reporte sin stock; hay compromisos abiertos sobre ellos.
cur.execute('SELECT DISTINCT pi."productoId" FROM "PedidoItem" pi JOIN "Pedido" p ON p.id=pi."pedidoId" WHERE p.estado IN (%s,%s)', ("validado","oc_generada"))
en_curso = {r[0] for r in cur.fetchall()}

# Mapa id->reservado actual (para no bajar stock por debajo de lo reservado).
cur.execute('SELECT id, reservado FROM "Producto"')
reservado_de = {pid: r for pid, r in cur.fetchall()}

prods = [(pid, cod) for pid, cod, *_ in filas_bak]
en_portal = {cod for _, cod in prods}
upd = act = inact = sin = bajo_reserva = 0
for pid, cod in prods:
    d = alila.get(cod)
    if not d:
        sin += 1
        # no apagar si tiene pedidos en curso
        if pid not in en_curso:
            cur.execute('UPDATE "Producto" SET activo=false WHERE id=%s', (pid,))
            inact += 1
        continue
    # stock real desde spkc (NO hjxq); nunca por debajo de lo reservado
    sd = sk.get(cod) or {}
    stock = to_int(sd.get("zl_kc")) or 0
    res = reservado_de.get(pid, 0)
    if stock < res:
        bajo_reserva += 1
        stock = res  # respetar reservas ya tomadas (y el CHECK reservado<=stock)
    activo = stock > 0 or pid in en_curso
    fotos = d.get("tp") or []
    foto1 = fotos[0] if fotos else None
    # reprice desde el costo real de AlilaTop (pf)
    costo = costo_alila(d)
    t1 = r100(costo*MARGEN[0]) if costo else None
    t2 = r100(costo*MARGEN[1]) if costo else None
    t3 = r100(costo*MARGEN[2]) if costo else None
    nombre = sin_chino(d.get("mc"))
    cat = clean_cat(d.get("x_lm"))
    cur.execute(
        'UPDATE "Producto" SET stock=%s, activo=%s, "fotos"=%s, "fotoUrl"=COALESCE(%s,"fotoUrl"),'
        ' nombre=COALESCE(%s,nombre), categoria=COALESCE(%s,categoria),'
        ' "descripcion"=%s, "dimensiones"=%s, "embalaje"=%s, "keywords"=%s, "nArticulo"=%s,'
        ' "codigoProveedor"=%s, "unidCaja"=COALESCE(%s,"unidCaja"), "linkML"=%s,'
        ' costo=COALESCE(%s,costo), "precioT1"=COALESCE(%s,"precioT1"),'
        ' "precioT2"=COALESCE(%s,"precioT2"), "precioT3"=COALESCE(%s,"precioT3") WHERE id=%s',
        (stock, activo, fotos, foto1, nombre, cat, sin_chino(d.get("sm")), traducir(clean(d.get("sp_cc"))),
         traducir(clean(d.get("bz_ss"))), clean(d.get("ss_cy")), clean(d.get("hh")),
         clean(d.get("gys_hjh")), to_int(d.get("zxs")), clean(d.get("ml_lj")),
         costo, t1, t2, t3, pid))
    upd += 1
    if activo: act += 1
    else: inact += 1

# 3) alta automatica de productos nuevos que cumplen el bar del catalogo
nuevos = 0
for cod, d in alila.items():
    if cod in en_portal:
        continue
    sd = sk.get(cod) or {}
    dem = to_int(sd.get("zxl")) or 0
    stock = to_int(sd.get("zl_kc")) or 0
    costo = costo_alila(d)
    if not (stock > 0 and dem >= PISO_DEMANDA and costo):
        continue
    c = campos_ricos(d, sd)
    if not c["nombre"]:
        continue  # sin nombre util, no publicar
    cur.execute(
        'INSERT INTO "Producto" (id,"codigoAlila",nombre,categoria,costo,"precioT1","precioT2","precioT3",'
        '"unidCaja","fotoUrl",fotos,descripcion,dimensiones,embalaje,keywords,"nArticulo",'
        '"codigoProveedor","linkML",activo,stock) '
        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        ("c" + uuid.uuid4().hex[:24], cod, c["nombre"], c["cat"], c["costo"], c["t1"], c["t2"], c["t3"],
         c["unidcaja"], c["foto1"], c["fotos"], c["desc"], c["dim"], c["emb"], c["kw"], c["narti"],
         c["codprov"], c["linkml"], True, c["stock"]))
    en_portal.add(cod)
    nuevos += 1
    act += 1

con.commit()
print(f"Portal: {len(prods)} productos | actualizados {upd} | sin match en Alila {sin}")
print(f"ALTAS nuevas (demanda>={PISO_DEMANDA}+stock+costo): {nuevos}")
print(f"ACTIVOS (con stock>0 o en curso): {act} | inactivos (sin stock): {inact}")
if bajo_reserva:
    print(f"OJO: {bajo_reserva} productos con stock AlilaTop < reservado (se mantuvo el reservado)")
cur.close(); con.close()
