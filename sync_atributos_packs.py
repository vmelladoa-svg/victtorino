"""
Sincroniza atributos SAFE en los 2 packs lavaplatos (gold_pro + gold_pro).
SAFE = ALPHANUMERIC_MODEL, MODEL, KITCHEN_SINKS_TYPE

Modo dry_run=True por defecto: muestra payload y simula con GET.
dry_run=False: ejecuta PUT /items/{id} con verificación pre/post.

Uso:
  python sync_atributos_packs.py            # dry run
  python sync_atributos_packs.py --execute  # real
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).parent
RAW = json.loads((ROOT / "data" / "auditoria" / "raw_fichas.json").read_text(encoding="utf-8"))

TOK_C2 = json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"]
H_C2 = {"Authorization": f"Bearer {TOK_C2}", "Content-Type": "application/json"}

SAFE_IDS = ["ALPHANUMERIC_MODEL", "MODEL", "KITCHEN_SINKS_TYPE"]

# Pares (winner, loser, label)
PAIRS = [
    ("MLC3779834584", "MLC1900464793", "Pack 37x32 + llave lavacopa"),
    ("MLC3779796948", "MLC3798052582", "Pack 80x44 + monomando"),
]


def attr_from_winner(win_attrs, attr_id):
    """Construye el attribute dict listo para PUT: incluye value_id si existe."""
    for a in win_attrs:
        if a.get("id") == attr_id:
            payload = {"id": attr_id}
            # value_id si está
            vid = a.get("value_id") or ((a.get("values") or [{}])[0].get("id"))
            vname = a.get("value_name") or ((a.get("values") or [{}])[0].get("name"))
            if vid:
                payload["value_id"] = vid
            if vname:
                payload["value_name"] = vname
            return payload
    return None


def build_plan():
    plans = []
    for wid, lid, label in PAIRS:
        w = RAW[wid]
        l = RAW[lid]
        w_attrs_list = w.get("attributes") or []
        l_attrs = {a["id"]: a for a in (l.get("attributes") or [])}
        attrs_payload = []
        diff_lines = []
        for aid in SAFE_IDS:
            new_attr = attr_from_winner(w_attrs_list, aid)
            if not new_attr:
                continue
            # Valor actual en perdedor
            old = l_attrs.get(aid)
            old_val = (old.get("value_name") if old else None) or "—"
            new_val = new_attr.get("value_name")
            if old and old.get("value_name") == new_val:
                continue  # ya está sync
            attrs_payload.append(new_attr)
            diff_lines.append(f"  {aid:<24s}  '{old_val}'  →  '{new_val}'")
        plans.append({
            "label": label,
            "winner_id": wid,
            "loser_id": lid,
            "payload": {"attributes": attrs_payload},
            "diff_lines": diff_lines,
        })
    return plans


def get_item(iid):
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,title,attributes"},
        headers=H_C2, timeout=15,
    )
    return r.status_code, (r.json() if r.status_code == 200 else r.text[:300])


def put_item(iid, payload):
    r = requests.put(
        f"https://api.mercadolibre.com/items/{iid}",
        json=payload, headers=H_C2, timeout=20,
    )
    body = None
    try:
        body = r.json()
    except Exception:
        body = r.text[:500]
    return r.status_code, body


def main(execute=False):
    plans = build_plan()
    print(f"=== Plan SAFE sync — {'EJECUTANDO' if execute else 'DRY-RUN'} ===\n")

    log = []
    for pl in plans:
        print(f"── {pl['label']} ──")
        print(f"  Loser ID: {pl['loser_id']}  (C2)")
        print(f"  Winner ID: {pl['winner_id']}  (C3)")
        print("  Cambios:")
        for line in pl["diff_lines"]:
            print(line)
        print(f"  Payload: {json.dumps(pl['payload'], ensure_ascii=False)}")

        if not execute:
            print("  [dry-run — no se envía PUT]\n")
            log.append({"item": pl["loser_id"], "status": "DRY_RUN",
                       "payload": pl["payload"], "diff": pl["diff_lines"]})
            continue

        # Pre
        sc, pre = get_item(pl["loser_id"])
        if sc != 200:
            print(f"  ✗ GET pre falló {sc}: {pre}")
            log.append({"item": pl["loser_id"], "status": "PRE_FAIL", "detail": str(pre)})
            continue

        # PUT
        sc, body = put_item(pl["loser_id"], pl["payload"])
        if sc != 200:
            print(f"  ✗ PUT falló {sc}: {body}")
            log.append({"item": pl["loser_id"], "status": "PUT_FAIL",
                       "http": sc, "detail": body, "payload": pl["payload"]})
            continue

        time.sleep(0.5)
        # Post
        sc2, post = get_item(pl["loser_id"])
        # Verificar que los 3 atributos quedaron como esperado
        post_attrs = {a["id"]: a for a in (post.get("attributes") or [])} if isinstance(post, dict) else {}
        ok_count = 0
        for new_attr in pl["payload"]["attributes"]:
            aid = new_attr["id"]
            expected = new_attr.get("value_name")
            actual = (post_attrs.get(aid) or {}).get("value_name")
            if actual == expected:
                ok_count += 1
        marker = "✓" if ok_count == len(pl["payload"]["attributes"]) else "~"
        print(f"  {marker} PUT OK | {ok_count}/{len(pl['payload']['attributes'])} atributos verificados\n")
        log.append({
            "item": pl["loser_id"], "status": "OK" if marker == "✓" else "PARTIAL",
            "verified": ok_count, "total": len(pl["payload"]["attributes"]),
            "payload": pl["payload"],
        })
        time.sleep(0.4)

    if execute:
        out = ROOT / "data" / "auditoria" / f"sync_atributos_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        out.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nLOG: {out}")


if __name__ == "__main__":
    execute = "--execute" in sys.argv
    main(execute=execute)
