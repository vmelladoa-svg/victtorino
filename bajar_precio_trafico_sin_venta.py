"""
Baja precio -10% (redondeado a cifra "limpia") en los items con alto tráfico
y 0 ventas 180d. Pre/post verification.

Usa --dry-run para ver qué se haría, --execute para aplicar.
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).parent
LOG_OUT = ROOT / "data" / "auditoria" / f"bajar_precio_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

TOK = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}

# Lista exacta del análisis previo (7 items con >=50 visitas y 0 ventas 180d)
# (item_id, cuenta, precio_actual, precio_nuevo_sugerido)
ITEMS = [
    ("MLC2276284008", "C3", 47884, 43000),   # Lavamanos vidrio
    ("MLC3903951470", "C1", 147269, 132000), # Shower Door 80x80
    ("MLC2713884324", "C3", 198990, 179000), # Shower Door 90x90
    ("MLC3738773726", "C2", 59990, 54000),   # Espejo LED
    ("MLC2998555490", "C3", 187690, 169000), # Shower Door 80x80x195
    ("MLC1893675967", "C3", 84624, 76000),   # Pack Lavaplatos
    ("MLC1629289257", "C1", 1193, 1100),     # Rollo papel C1 (era ROI- en upgrade — vale probar precio)
]


def get_item(cuenta, iid):
    h = {"Authorization": f"Bearer {TOK[cuenta]}"}
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,title,price,available_quantity,status,listing_type_id"},
        headers=h, timeout=15,
    )
    return r.status_code, (r.json() if r.status_code == 200 else r.text[:300])


def put_price(cuenta, iid, new_price):
    h = {"Authorization": f"Bearer {TOK[cuenta]}", "Content-Type": "application/json"}
    r = requests.put(
        f"https://api.mercadolibre.com/items/{iid}",
        json={"price": new_price}, headers=h, timeout=20,
    )
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text[:500]


def main(execute=False):
    print(f"=== {'EJECUTANDO' if execute else 'DRY-RUN'} — bajar precio en {len(ITEMS)} items ===\n")
    log = []

    for i, (iid, cuenta, p_old, p_new) in enumerate(ITEMS, 1):
        print(f"[{i}/{len(ITEMS)}] {cuenta} {iid}")
        sc, pre = get_item(cuenta, iid)
        if sc != 200:
            print(f"  ✗ GET pre falló: {sc}")
            log.append({"item": iid, "cuenta": cuenta, "status": "PRE_FAIL", "detail": str(pre)})
            continue
        actual_price = pre.get("price")
        actual_stock = pre.get("available_quantity", 0)
        status = pre.get("status")
        title = (pre.get("title") or "")[:55]
        print(f"  TITULO: {title}")
        print(f"  PRE: precio=${actual_price:,} stock={actual_stock} status={status}")

        if status != "active":
            print(f"  ⊘ status={status} — skip")
            log.append({"item": iid, "cuenta": cuenta, "status": "SKIP_INACTIVE", "actual_status": status})
            continue
        if actual_stock == 0:
            print(f"  ⊘ sin stock — skip")
            log.append({"item": iid, "cuenta": cuenta, "status": "SKIP_NO_STOCK"})
            continue
        if actual_price == p_new:
            print(f"  ⊘ precio ya está en ${p_new:,} — skip")
            log.append({"item": iid, "cuenta": cuenta, "status": "SKIP_SAME_PRICE"})
            continue

        delta = p_new - actual_price
        delta_pct = delta / actual_price * 100
        print(f"  CAMBIO: ${actual_price:,} → ${p_new:,}  ({delta:+,} CLP = {delta_pct:+.1f}%)")

        if not execute:
            print(f"  [dry-run]\n")
            log.append({"item": iid, "cuenta": cuenta, "status": "DRY_RUN",
                       "old_price": actual_price, "new_price": p_new, "delta_pct": round(delta_pct,2)})
            continue

        sc, body = put_price(cuenta, iid, p_new)
        if sc != 200:
            print(f"  ✗ PUT falló {sc}: {body}")
            log.append({"item": iid, "cuenta": cuenta, "status": "PUT_FAIL",
                       "http": sc, "detail": str(body)[:300]})
            time.sleep(0.4)
            continue
        time.sleep(0.5)
        sc, post = get_item(cuenta, iid)
        post_price = post.get("price") if isinstance(post, dict) else None
        ok = sc == 200 and post_price == p_new
        marker = "✓" if ok else "~"
        print(f"  {marker} POST: precio=${post_price:,}")
        log.append({"item": iid, "cuenta": cuenta,
                   "status": "OK" if ok else "POST_MISMATCH",
                   "pre_price": actual_price, "post_price": post_price,
                   "delta_pct": round(delta_pct,2)})
        time.sleep(0.4)
        print()

    LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOG_OUT.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for x in log if x["status"] == "OK")
    fail = sum(1 for x in log if "FAIL" in x["status"] or "MISMATCH" in x["status"])
    skip = sum(1 for x in log if "SKIP" in x["status"])
    dry = sum(1 for x in log if x["status"] == "DRY_RUN")
    print(f"\n=== Resumen ===")
    print(f"OK: {ok} | FAIL: {fail} | SKIP: {skip} | DRY: {dry}")
    print(f"LOG: {LOG_OUT}")


if __name__ == "__main__":
    main(execute=("--execute" in sys.argv))
