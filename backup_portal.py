# -*- coding: utf-8 -*-
"""Respaldo logico diario de la base del Portal Mayorista (Neon).
Vuelca TODAS las tablas a JSON en data/backups/full_<timestamp>/. Independiente del
plan de Neon: es la red de recuperacion si la base se vacia o se corrompe.
Restaurar con restaurar_portal.py. Pensado para Tarea Programada de Windows (diario)."""
import psycopg2, json, re, shutil, os
from pathlib import Path
from datetime import datetime, timezone

# ROOT = carpeta del script (funciona en el PC y en GitHub Actions).
ROOT = Path(__file__).resolve().parent
# DATABASE_URL: variable de entorno (nube) o, si no, el .env local (PC).
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    ENV = (ROOT / "portal-mayorista" / ".env").read_text(encoding="utf-8")
    DB_URL = re.search(r'DATABASE_URL="([^"]+)"', ENV).group(1)
HOST = re.search(r'@([^/]+)/', DB_URL).group(1)

# orden FK-seguro para volcar (padres primero); restaurar usa el mismo orden
TABLAS = ["Comerciante", "Producto", "Pedido", "PedidoItem", "OC"]
KEEP = 14  # conservar los ultimos N respaldos

con = psycopg2.connect(DB_URL); cur = con.cursor()
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
dest = ROOT / "data" / "backups" / f"full_{ts}"
dest.mkdir(parents=True, exist_ok=True)

meta = {"fecha": datetime.now(timezone.utc).isoformat(), "host": HOST, "tablas": []}
for t in TABLAS:
    cur.execute(f'SELECT * FROM "{t}"')
    cols = [c.name for c in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    (dest / f"{t}.json").write_text(
        json.dumps(rows, ensure_ascii=False, default=str, indent=1), encoding="utf-8")
    meta["tablas"].append(f"{t}: {len(rows)}")
(dest / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
cur.close(); con.close()
print(f"Respaldo OK: {dest.name}")
for x in meta["tablas"]: print("  ", x)

# poda: dejar solo los ultimos KEEP
backs = sorted((ROOT / "data" / "backups").glob("full_*"), key=lambda p: p.name)
for old in backs[:-KEEP]:
    shutil.rmtree(old, ignore_errors=True)
    print("  podado:", old.name)
