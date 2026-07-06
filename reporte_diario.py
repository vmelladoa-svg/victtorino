# -*- coding: utf-8 -*-
"""Reporte diario del Portal Mayorista por WhatsApp (CallMeBot).
Corre en GitHub Actions DESPUES de refrescar_inventario.py. Solo lee la base."""
import os, re, csv, glob, requests, psycopg2
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
UMBRAL = 0.25
TOP = 8
PHONE = os.environ.get("CALLMEBOT_PHONE")
APIKEY = os.environ.get("CALLMEBOT_APIKEY")
SYNC = os.environ.get("SYNC_STATUS", "desconocido")
DB_URL = os.environ.get("DATABASE_URL")

_CJK = re.compile(r'[぀-ヿ㐀-䶿一-鿿豈-﫿＀-￯]')

def tiene_chino(*vals):
    return any(v and _CJK.search(str(v)) for v in vals)

def tiene_alila(*vals):
    return any(v and 'alila' in str(v).lower() for v in vals)

def foto_de_alila(url, fotos):
    cand = [url] + (list(fotos) if fotos else [])
    return any(u and ('alila' in str(u).lower() or 'bspapp' in str(u).lower()) for u in cand)

def nom(r):
    return str(r[2] or r[1] or r[0])[:32]

def enviar(texto):
    print("----- REPORTE -----\n" + texto + "\n-------------------")
    if not (PHONE and APIKEY):
        print("Sin CALLMEBOT_PHONE/APIKEY: no se envia WhatsApp."); return
    try:
        r = requests.get("https://api.callmebot.com/whatsapp.php",
                         params={"phone": PHONE, "apikey": APIKEY, "text": texto}, timeout=40)
        print("CallMeBot:", r.status_code, str(r.text)[:200])
    except Exception as e:
        print("Error CallMeBot:", e)

fecha = datetime.now().strftime("%d-%m-%Y")

if not DB_URL:
    enviar("ALERTA Portal Mayorista " + fecha + ": falta DATABASE_URL, revisar."); raise SystemExit(0)

try:
    con = psycopg2.connect(DB_URL); cur = con.cursor()
    cur.execute('SELECT id, "codigoAlila", nombre, costo, "precioT1", descripcion, "fotoUrl", fotos, activo, stock FROM "Producto"')
    rows = cur.fetchall(); cur.close(); con.close()
except Exception as e:
    enviar("ALERTA Portal Mayorista " + fecha + ": no se pudo conectar a la base (" + str(e)[:80] + "). El sync no actualizo."); raise SystemExit(0)

total = len(rows)
activos = sum(1 for r in rows if r[8])
sin_stock = [r for r in rows if (r[9] or 0) == 0]
sin_desc = [r for r in rows if r[8] and (not r[5] or not str(r[5]).strip())]
chino = [r for r in rows if tiene_chino(r[2], r[5])]
alila_txt = [r for r in rows if tiene_alila(r[2], r[5])]
fotos_alila = [r for r in rows if foto_de_alila(r[6], r[7])]
precio_malo = [r for r in rows if r[8] and (not r[4] or (r[4] or 0) <= 0)]

old = {}
csvs = sorted(glob.glob(str(ROOT / "data" / "backups" / "productos_*.csv")))
if csvs:
    with open(csvs[-1], encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try: old[row["id"]] = float(row["precioT1"] or 0)
            except Exception: pass

movs = []; nuevos = 0
for r in rows:
    pid, nombre, t1new = r[0], r[2], r[4]
    if pid not in old:
        nuevos += 1; continue
    t1old = old.get(pid) or 0
    if t1old > 0 and t1new:
        d = (float(t1new) - t1old) / t1old
        if abs(d) >= UMBRAL:
            movs.append((str(nombre or pid)[:32], d))
movs.sort(key=lambda x: -abs(x[1]))

L = []
L.append("Reporte Portal Mayorista " + fecha)
L.append("Sync: " + ("OK" if SYNC == "success" else "REVISAR (" + SYNC + ")"))
L.append("Productos: " + str(total) + " total, " + str(activos) + " activos, " + str(len(sin_stock)) + " sin stock")
L.append("Precios reajustados al costo Alila. Movimientos de 25 por ciento o mas: " + str(len(movs)))
for nombre, d in movs[:TOP]:
    L.append("  - " + nombre + ": " + str(round(d*100)) + " por ciento " + ("subio" if d > 0 else "bajo"))
L.append("Calidad: " + str(len(chino)) + " con chino, " + str(len(alila_txt)) + " con Alila en texto, " + str(len(sin_desc)) + " sin descripcion")
L.append("Fotos desde CDN Alila: " + str(len(fotos_alila)))
if precio_malo:
    L.append("OJO precios invalidos (0 o nulo): " + str(len(precio_malo)))
L.append("Altas nuevas: " + str(nuevos))
if sin_stock:
    L.append("Sin stock: " + ", ".join(nom(r) for r in sin_stock[:TOP]) + (" ..." if len(sin_stock) > TOP else ""))

enviar("\n".join(L))
