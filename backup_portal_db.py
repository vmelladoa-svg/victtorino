# -*- coding: utf-8 -*-
"""Respaldo lógico completo de la base Neon del Portal Mayorista.
Vuelca TODAS las tablas a un .sql con INSERTs restaurables (psql/python).
Pensado para correr a diario por Tarea Programada, ANTES del refresco de inventario.
Rota: conserva los ultimos 14 respaldos."""
import re, psycopg2
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\dell\victtorino")
URL = re.search(r'DATABASE_URL="([^"]+)"', (ROOT / "portal-mayorista" / ".env").read_text(encoding="utf-8")).group(1)
OUT = ROOT / "data" / "backups"
OUT.mkdir(parents=True, exist_ok=True)

con = psycopg2.connect(URL); cur = con.cursor()
cur.execute("SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")
tables = [r[0] for r in cur.fetchall()]

fn = OUT / f"portal_full_{datetime.now():%Y%m%d_%H%M%S}.sql"
total = 0
with open(fn, "w", encoding="utf-8") as f:
    f.write(f"-- Backup Portal Mayorista (Neon) {datetime.now().isoformat()}\n")
    f.write("-- Restaurar: psql <URL> -f este_archivo.sql  (o por psycopg2)\n")
    for t in tables:
        cur.execute(f'SELECT * FROM "{t}"')
        rows = cur.fetchall()
        cols = ",".join(f'"{d[0]}"' for d in cur.description)
        f.write(f'\n-- {t}: {len(rows)} filas\n')
        for row in rows:
            vals = cur.mogrify(",".join(["%s"] * len(row)), row).decode("utf-8")
            f.write(f'INSERT INTO "{t}" ({cols}) VALUES ({vals});\n')
        total += len(rows)
cur.close(); con.close()

# rotacion: dejar los ultimos 14
backs = sorted(OUT.glob("portal_full_*.sql"))
for old in backs[:-14]:
    old.unlink()

print(f"Backup OK: {fn.name} | {len(tables)} tablas | {total} filas | conservados {min(len(backs),14)}")
