"""
Monitor: detecta actividad nueva en las 3 cuentas ML cada 60s.
Emite UNA linea cuando aparece:
  - Nueva pregunta UNANSWERED
  - Nueva orden creada en la ultima hora
  - Pregunta que paso de UNANSWERED a ANSWERED (significa que Victoria publico)

Stdout = stream de eventos para el monitor.
"""
import sys
import io
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
ML = "https://api.mercadolibre.com"
LBL = {"c1": "C1", "c2": "C2", "c3": "C3"}
CUENTAS = [("c1", ROOT / "tokens_cuenta1.json"),
           ("c2", ROOT / "tokens_cuenta2.json"),
           ("c3", ROOT / "tokens_cuenta3.json")]


def get_token(path):
    return json.loads(path.read_text(encoding="utf-8"))["access_token"]


def get_uid(path):
    return json.loads(path.read_text(encoding="utf-8"))["user_id"]


def fetch_unanswered(token):
    """Set de question_ids UNANSWERED."""
    try:
        r = requests.get(
            f"{ML}/my/received_questions/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"status": "UNANSWERED", "limit": 50}, timeout=15)
        if r.status_code != 200: return None
        return {(q["id"], q.get("text", "")[:60], (q.get("item_id") or ""))
                for q in r.json().get("questions", [])}
    except Exception: return None


def fetch_recent_orders(token, uid, minutos=120):
    """Ordenes creadas en los ultimos N minutos."""
    desde = (datetime.now(timezone.utc) - timedelta(minutes=minutos)).strftime(
        "%Y-%m-%dT%H:%M:%S.000-00:00")
    try:
        r = requests.get(f"{ML}/orders/search",
                         headers={"Authorization": f"Bearer {token}"},
                         params={"seller": uid, "order.date_created.from": desde,
                                 "sort": "date_desc", "limit": 20},
                         timeout=15)
        if r.status_code != 200: return None
        res = []
        for o in r.json().get("results", []):
            buyer = (o.get("buyer") or {})
            items = o.get("order_items") or []
            tit = items[0]["item"]["title"][:60] if items else ""
            res.append((o["id"], (buyer.get("first_name") or "Cliente"), tit))
        return res
    except Exception: return None


# Estado inicial: snapshot de lo que ya hay (no notifica esto)
prev_unans = {}
prev_orders = {}
print(f"[{datetime.now():%H:%M:%S}] watch iniciado — pollea cada 60s las 3 cuentas ML",
      flush=True)
for c, tp in CUENTAS:
    token = get_token(tp); uid = get_uid(tp)
    prev_unans[c] = fetch_unanswered(token) or set()
    orders = fetch_recent_orders(token, uid, minutos=120) or []
    prev_orders[c] = {o[0] for o in orders}
    print(f"  baseline {LBL[c]}: {len(prev_unans[c])} preg pendientes, "
          f"{len(prev_orders[c])} ords ultimas 2h", flush=True)

while True:
    time.sleep(60)
    for c, tp in CUENTAS:
        try:
            token = get_token(tp); uid = get_uid(tp)
        except Exception as e:
            print(f"[{datetime.now():%H:%M:%S}] {LBL[c]} ERROR cargando token: {e}", flush=True)
            continue

        # Preguntas
        cur_unans = fetch_unanswered(token)
        if cur_unans is None:
            print(f"[{datetime.now():%H:%M:%S}] {LBL[c]} preg: API ERROR (timeout o auth)", flush=True)
        else:
            ids_prev = {q[0] for q in prev_unans[c]}
            ids_cur = {q[0] for q in cur_unans}
            for q in cur_unans:
                if q[0] not in ids_prev:
                    print(f"[{datetime.now():%H:%M:%S}] NUEVA PREGUNTA {LBL[c]} qid={q[0]} item={q[2]} texto={q[1]!r}",
                          flush=True)
            for q in prev_unans[c]:
                if q[0] not in ids_cur:
                    print(f"[{datetime.now():%H:%M:%S}] PREGUNTA RESPONDIDA {LBL[c]} qid={q[0]} (Victoria publico)",
                          flush=True)
            prev_unans[c] = cur_unans

        # Ordenes
        cur_orders = fetch_recent_orders(token, uid, minutos=120)
        if cur_orders is None:
            print(f"[{datetime.now():%H:%M:%S}] {LBL[c]} ord: API ERROR", flush=True)
        else:
            ids_prev = prev_orders[c]
            for o in cur_orders:
                if o[0] not in ids_prev:
                    print(f"[{datetime.now():%H:%M:%S}] NUEVA ORDEN {LBL[c]} order_id={o[0]} comprador={o[1]} producto={o[2]!r}",
                          flush=True)
            prev_orders[c] = {o[0] for o in cur_orders}
