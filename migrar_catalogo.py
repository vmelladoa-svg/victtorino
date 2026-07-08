# -*- coding: utf-8 -*-
"""Migracion: independiza el catalogo EXISTENTE de Alila.
Para cada producto: sube sus fotos (las URLs Alila guardadas en la columna fotos)
a Cloudinary, limpia la descripcion (sin chino/HTML/rastros) y borra linkML.
Idempotente: si un producto ya tiene fotos en Cloudinary, no las re-sube.

Controles (env, opcionales):
 - MIGRAR_CODIGOS="6000028,6000152"  -> migra solo esos (para probar)
 - MIGRAR_LIMIT="5"                  -> migra como maximo N (para probar)
Sin ninguno => migra TODO el catalogo."""
import os, re, psycopg2
import catalogo_utils as U

DB_URL = os.environ["DATABASE_URL"]
LIMIT = int(os.environ.get("MIGRAR_LIMIT", "0"))
SOLO = os.environ.get("MIGRAR_CODIGOS", "").strip()
solo = {c for c in re.split(r'[\s,;]+', SOLO) if c} if SOLO else None

con = psycopg2.connect(DB_URL); cur = con.cursor()
cur.execute('SELECT id, "codigoAlila", fotos, "fotoUrl", descripcion FROM "Producto" ORDER BY "codigoAlila"')
rows = cur.fetchall()
print(f"Productos en portal: {len(rows)}")

proc = migradas_fotos = ya_ok = 0
for pid, cod, fotos, fotoUrl, desc in rows:
    if solo and cod not in solo:
        continue
    if LIMIT and proc >= LIMIT:
        break
    ya = bool(fotoUrl) and "res.cloudinary.com" in str(fotoUrl)
    urls = fotos if isinstance(fotos, list) else []
    if ya:
        nuevas = urls          # ya estan en Cloudinary
        ya_ok += 1
    else:
        nuevas = U.rehost_fotos(cod, urls)
        if nuevas: migradas_fotos += 1
    desc_limpia = U.limpiar_desc(desc)
    cur.execute(
        'UPDATE "Producto" SET fotos=%s, "fotoUrl"=%s, descripcion=%s, "linkML"=NULL WHERE id=%s',
        (nuevas, (nuevas[0] if nuevas else None), desc_limpia, pid))
    con.commit()               # commit por producto (migracion larga, reanudable)
    proc += 1
    print(f"[{cod}] fotos {len(urls)}->{len(nuevas)} {'(ya cloudinary)' if ya else ''} | desc {'ok' if desc_limpia else 'vacia'}")

cur.close(); con.close()
print(f"\n=== MIGRACION ===")
print(f"Procesados:        {proc}")
print(f"Con fotos subidas: {migradas_fotos}")
print(f"Ya en Cloudinary:  {ya_ok}")
