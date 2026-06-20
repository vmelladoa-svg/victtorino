"""
Auditoria integral ML — 3 cuentas (C1, C2, C3).
Genera snapshot JSON con publicaciones, reputacion, ventas, preguntas y reclamos.
Output: data/auditoria/snapshot_<cuenta>.json
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
import requests

ROOT = Path(__file__).parent
OUT  = ROOT / "data" / "auditoria"
OUT.mkdir(parents=True, exist_ok=True)

ML = "https://api.mercadolibre.com"
CUENTAS = [
    ("C1", "PREMIUMGRIFERIAS1", ROOT / "tokens_cuenta1.json"),
    ("C2", "VICTTORINOOFICIAL2", ROOT / "tokens_cuenta2.json"),
    ("C3", "NOVAGRIFERIAS3",    ROOT / "tokens_cuenta3.json"),
]
DIAS_VENTAS = 180


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _get(token, path, params=None):
    r = requests.get(f"{ML}{path}", headers={"Authorization": f"Bearer {token}"},
                     params=params or {}, timeout=20)
    return r


def _all_items_ids(token, user_id):
    """GET /users/{id}/items/search con scroll. Solo IDs."""
    ids, scroll = [], None
    while True:
        params = {"search_type": "scan", "limit": 100}
        if scroll: params["scroll_id"] = scroll
        r = _get(token, f"/users/{user_id}/items/search", params)
        if r.status_code != 200:
            break
        j = r.json()
        results = j.get("results") or []
        ids.extend(results)
        scroll = j.get("scroll_id")
        if not scroll or not results:
            break
        time.sleep(0.05)
    return ids


def _multiget_items(token, ids, attrs=None):
    """GET /items?ids=... (multi-get, max 20 por llamada)."""
    items = []
    base_params = {}
    if attrs:
        base_params["attributes"] = attrs
    for i in range(0, len(ids), 20):
        chunk = ids[i:i+20]
        params = dict(base_params, ids=",".join(chunk))
        r = _get(token, "/items", params)
        if r.status_code != 200:
            continue
        for entry in r.json():
            if entry.get("code") == 200 and entry.get("body"):
                items.append(entry["body"])
        time.sleep(0.05)
    return items


def _visits(token, ids, days=30):
    """GET /items/visits/time_window?ids=... resuelve N items en una llamada."""
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i+50]
        r = _get(token, "/items/visits/time_window", {
            "ids": ",".join(chunk),
            "last": days,
            "unit": "day",
        })
        if r.status_code != 200:
            continue
        for it in r.json():
            out[it.get("item_id")] = it.get("total_visits", 0)
        time.sleep(0.05)
    return out


def _orders(token, seller_id, days=DIAS_VENTAS):
    """GET /orders/search con date_from. Retorna lista completa via paginacion."""
    desde = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%dT%H:%M:%S.000-00:00"
    )
    out, offset = [], 0
    while True:
        r = _get(token, "/orders/search", {
            "seller": seller_id,
            "order.date_created.from": desde,
            "sort": "date_desc",
            "limit": 50,
            "offset": offset,
        })
        if r.status_code != 200:
            break
        j = r.json()
        results = j.get("results") or []
        out.extend(results)
        total = j.get("paging", {}).get("total", 0)
        offset += 50
        if offset >= total or not results:
            break
        time.sleep(0.05)
    return out


def _reputation(token, user_id):
    r = _get(token, f"/users/{user_id}")
    if r.status_code != 200: return {}
    j = r.json()
    rep = j.get("seller_reputation") or {}
    return {
        "user_id": user_id,
        "nickname": j.get("nickname"),
        "registration_date": j.get("registration_date"),
        "level_id": rep.get("level_id"),
        "power_seller_status": rep.get("power_seller_status"),
        "metrics": rep.get("metrics"),
        "transactions": rep.get("transactions"),
    }


def _questions_recent(token, user_id, days=90):
    """Conteo de preguntas recibidas (sin paginar todo)."""
    desde = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%dT%H:%M:%S.000-00:00"
    )
    r = _get(token, "/my/received_questions/search", {
        "status": "ANSWERED",
        "limit": 1,
        "date_created.from": desde,
    })
    answered = r.json().get("total", 0) if r.status_code == 200 else 0
    r2 = _get(token, "/my/received_questions/search", {
        "status": "UNANSWERED",
        "limit": 1,
    })
    unanswered = r2.json().get("total", 0) if r2.status_code == 200 else 0
    return {"answered_180d": answered, "unanswered_now": unanswered}


def auditar(nombre, alias, token_path):
    print(f"\n=== {nombre} ({alias}) ===")
    creds = _load(token_path)
    token, uid = creds["access_token"], creds["user_id"]

    print(f"  Reputacion...")
    rep = _reputation(token, uid)

    print(f"  Items IDs...")
    ids = _all_items_ids(token, uid)
    print(f"     {len(ids)} items totales")

    print(f"  Detalle de items...")
    items = _multiget_items(token, ids,
                            attrs="id,title,price,base_price,available_quantity,sold_quantity,"
                                  "category_id,status,sub_status,listing_type_id,pictures,health,"
                                  "shipping,permalink,start_time,seller_custom_field")
    actives = [i for i in items if i.get("status") == "active"]
    print(f"     {len(items)} traidos, {len(actives)} activos")

    print(f"  Visitas 30d...")
    visits = _visits(token, [i["id"] for i in actives], days=30)

    print(f"  Ordenes ultimos {DIAS_VENTAS}d...")
    orders = _orders(token, uid, days=DIAS_VENTAS)
    print(f"     {len(orders)} ordenes")

    print(f"  Preguntas...")
    qs = _questions_recent(token, uid, days=DIAS_VENTAS)

    snapshot = {
        "meta": {
            "cuenta": nombre,
            "alias": alias,
            "user_id": uid,
            "extraido": datetime.utcnow().isoformat() + "Z",
            "dias_ventas": DIAS_VENTAS,
        },
        "reputacion": rep,
        "items": items,
        "items_activos": [i["id"] for i in actives],
        "visitas_30d": visits,
        "orders": orders,
        "preguntas": qs,
    }
    out_file = OUT / f"snapshot_{nombre.lower()}.json"
    out_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  OK  {out_file}  ({out_file.stat().st_size//1024} KB)")


if __name__ == "__main__":
    for nombre, alias, tp in CUENTAS:
        try:
            auditar(nombre, alias, tp)
        except Exception as e:
            print(f"  ERROR {nombre}: {e}")
    print("\n=== Snapshot listo en data/auditoria/ ===")
