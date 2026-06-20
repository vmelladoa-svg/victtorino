"""
Ejecuta upgrade gold_special → gold_pro en los 12 SKUs ROI-positivo del dry-run.
Lee replicacion_upgrade_dryrun.xlsx, filtra Net 180d > 0 y Needs Upgrade=True.
Para cada uno:
  1. GET item antes (verificar estado actual)
  2. POST /items/{id}/listing_type con {"id":"gold_pro"}
  3. GET item después (verificar cambio)
  4. Log JSON con resultado por item

Output: data/auditoria/upgrade_listing_<fecha>.json
"""
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests

import sys
ROOT = Path(__file__).parent
DRYRUN_DEFAULT = ROOT / "replicacion_upgrade_dryrun.xlsx"
# Acepta --file <ruta> como override
DRYRUN = DRYRUN_DEFAULT
for i, a in enumerate(sys.argv):
    if a == "--file" and i+1 < len(sys.argv):
        DRYRUN = ROOT / sys.argv[i+1]
LOG_OUT = ROOT / "data" / "auditoria" / f"upgrade_listing_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

TOK_C1 = json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"]
TOK_C2 = json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"]
TOKENS = {"C1": TOK_C1, "C2": TOK_C2}


def get_item(cuenta, iid):
    h = {"Authorization": f"Bearer {TOKENS[cuenta]}"}
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,title,listing_type_id,status,price"},
        headers=h, timeout=15,
    )
    return r.status_code, (r.json() if r.status_code == 200 else r.text[:300])


def upgrade(cuenta, iid):
    h = {"Authorization": f"Bearer {TOKENS[cuenta]}", "Content-Type": "application/json"}
    r = requests.post(
        f"https://api.mercadolibre.com/items/{iid}/listing_type",
        json={"id": "gold_pro"},
        headers=h, timeout=20,
    )
    return r.status_code, (r.json() if r.text else None)


def main():
    df = pd.read_excel(DRYRUN)
    # Filtro: ROI positivo + needs upgrade
    target = df[(df["Needs Upgrade"]) & (df["Net 180d CLP"].fillna(-1) > 0)].copy()
    target = target.sort_values("Net 180d CLP", ascending=False)
    print(f"Target: {len(target)} SKUs ROI-positivo a upgrade gold_special → gold_pro")
    for _, r in target.iterrows():
        print(f"  {r['Cuenta']} {r['Lose ItemID']} | {r['Producto'][:35]} | net ${int(r['Net 180d CLP']):,}")
    print()

    log = []
    for i, (_, r) in enumerate(target.iterrows(), 1):
        iid = r["Lose ItemID"]
        cuenta = r["Cuenta"]
        prod = r["Producto"]
        net = int(r["Net 180d CLP"]) if pd.notna(r["Net 180d CLP"]) else None
        print(f"\n[{i}/{len(target)}] {cuenta} {iid}  {prod[:40]}")

        # Pre
        sc_pre, pre = get_item(cuenta, iid)
        if sc_pre != 200:
            print(f"  ✗ GET pre falló {sc_pre}: {pre}")
            log.append({"item": iid, "cuenta": cuenta, "status": "PRE_FAIL", "detail": str(pre)})
            continue
        print(f"  PRE: listing={pre.get('listing_type_id')} status={pre.get('status')}")

        # Si ya está en gold_pro, skip
        if pre.get("listing_type_id") == "gold_pro":
            print(f"  ⊘ Ya está en gold_pro — skip")
            log.append({"item": iid, "cuenta": cuenta, "status": "SKIP_ALREADY", "pre": pre})
            continue

        # Upgrade
        sc_up, body_up = upgrade(cuenta, iid)
        if sc_up != 200:
            print(f"  ✗ Upgrade falló {sc_up}: {body_up}")
            log.append({"item": iid, "cuenta": cuenta, "status": "UPGRADE_FAIL",
                        "http": sc_up, "detail": body_up, "pre": pre})
            continue

        time.sleep(0.5)

        # Post
        sc_post, post = get_item(cuenta, iid)
        ok = sc_post == 200 and post.get("listing_type_id") == "gold_pro"
        marker = "✓" if ok else "?"
        print(f"  {marker} POST: listing={post.get('listing_type_id')}")
        log.append({
            "item": iid, "cuenta": cuenta,
            "status": "OK" if ok else "POST_MISMATCH",
            "pre_listing": pre.get("listing_type_id"),
            "post_listing": post.get("listing_type_id"),
            "upgrade_response": body_up,
            "producto": prod,
            "net_180d_proyectado": net,
        })
        time.sleep(0.4)

    LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOG_OUT.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== LOG: {LOG_OUT} ===")

    ok = sum(1 for x in log if x["status"] == "OK")
    fail = sum(1 for x in log if "FAIL" in x["status"] or "MISMATCH" in x["status"])
    skip = sum(1 for x in log if x["status"] == "SKIP_ALREADY")
    print(f"OK: {ok}  | Skip: {skip}  | Fail: {fail}")


if __name__ == "__main__":
    main()
