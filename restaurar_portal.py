# -*- coding: utf-8 -*-
"""Restaura la base del Portal Mayorista desde un respaldo de backup_portal.py.
Uso:  python restaurar_portal.py data\backups\full_2026-06-22T22-25-37
      python restaurar_portal.py <carpeta> --si   (sin confirmacion)
PELIGRO: reemplaza el contenido actual de las tablas. Pide confirmacion salvo --si."""
import psycopg2, json, re, sys
from pathlib import Path

ROOT = Path(r"C:\Users\dell\victtorino")
ENV = (ROOT / "portal-mayorista" / ".env").read_text(encoding="utf-8")
DB_URL = re.search(r'DATABASE_URL="([^"]+)"', ENV).group(1)

if len(sys.argv) < 2:
    raise SystemExit("Falta la carpeta del respaldo. Ej: python restaurar_portal.py data\\backups\\full_...")
src = Path(sys.argv[1])
if not src.is_absolute(): src = ROOT / src
auto = "--si" in sys.argv
if not (src / "_meta.json").exists():
    raise SystemExit(f"No es un respaldo valido: {src}")

meta = json.loads((src / "_meta.json").read_text(encoding="utf-8"))
print("Respaldo:", src.name, "| fecha", meta["fecha"]);
for x in meta["tablas"]: print("  ", x)

# borrar en orden inverso (hijos primero), insertar en orden directo (padres primero)
ORDEN = ["Comerciante", "Producto", "Pedido", "PedidoItem", "OC"]

if not auto:
    r = input(f'\nEsto REEMPLAZA las tablas de la base {DB_URL.split("@")[1].split("/")[0]}. Escribe "restaurar": ')
    if r.strip().lower() != "restaurar":
        raise SystemExit("Cancelado.")

con = psycopg2.connect(DB_URL); cur = con.cursor()
try:
    for t in reversed(ORDEN):
        cur.execute(f'DELETE FROM "{t}"')
    for t in ORDEN:
        rows = json.loads((src / f"{t}.json").read_text(encoding="utf-8"))
        for row in rows:
            cols = list(row.keys())
            ph = ",".join(["%s"] * len(cols))
            colsq = ",".join(f'"{c}"' for c in cols)
            cur.execute(f'INSERT INTO "{t}" ({colsq}) VALUES ({ph})', [row[c] for c in cols])
        print(f"  {t}: {len(rows)} filas restauradas")
    con.commit()
    print("Restauracion OK.")
except Exception as e:
    con.rollback()
    print("ERROR, se revirtio todo:", e); raise
finally:
    cur.close(); con.close()
