"""
PUT /items/{id} con nuevo title en los 30 items SEO.
Usa el diccionario CURATED de titulos_top30_curated.py.
Verificación pre/post + log.
"""
import json
import time
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).parent

# Importar diccionario CURATED
import sys
sys.path.insert(0, str(ROOT))
from titulos_top30_curated import CURATED, TOP30

TOK = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}


def get_item(cuenta, iid):
    h = {"Authorization": f"Bearer {TOK[cuenta]}"}
    r = requests.get(
        f"https://api.mercadolibre.com/items/{iid}",
        params={"attributes": "id,title,status,has_bids"},
        headers=h, timeout=15,
    )
    return r.status_code, (r.json() if r.status_code == 200 else r.text[:300])


def put_title(cuenta, iid, new_title):
    h = {"Authorization": f"Bearer {TOK[cuenta]}", "Content-Type": "application/json"}
    r = requests.put(
        f"https://api.mercadolibre.com/items/{iid}",
        json={"title": new_title}, headers=h, timeout=20,
    )
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text[:500]


def main():
    items_by_id = {it["iid"]: it for it in TOP30}
    log = []
    total = len(CURATED)

    for i, (iid, new_title) in enumerate(CURATED.items(), 1):
        it = items_by_id.get(iid)
        if not it:
            print(f"[{i}/{total}] {iid}: NO ENCONTRADO en TOP30")
            continue
        cuenta = it["cuenta"]
        print(f"\n[{i}/{total}] {cuenta} {iid}")
        print(f"  ANTES: {it['title']}")
        print(f"  NUEVO: {new_title}")

        sc, pre = get_item(cuenta, iid)
        if sc != 200:
            print(f"  ✗ GET pre falló {sc}: {pre}")
            log.append({"item": iid, "cuenta": cuenta, "status": "PRE_FAIL", "detail": str(pre)})
            continue
        if pre.get("has_bids"):
            print(f"  ⊘ has_bids:true — skip (ML no deja cambiar título con ofertas activas)")
            log.append({"item": iid, "cuenta": cuenta, "status": "SKIP_HAS_BIDS",
                       "pre_title": pre.get("title")})
            continue

        sc, body = put_title(cuenta, iid, new_title)
        if sc != 200:
            print(f"  ✗ PUT falló {sc}: {body}")
            log.append({"item": iid, "cuenta": cuenta, "status": "PUT_FAIL",
                       "http": sc, "detail": str(body)[:300], "pre_title": pre.get("title"),
                       "new_title": new_title})
            time.sleep(0.4)
            continue

        time.sleep(0.5)
        sc_p, post = get_item(cuenta, iid)
        post_title = post.get("title") if isinstance(post, dict) else None
        ok = sc_p == 200 and post_title == new_title
        print(f"  {'✓' if ok else '~'} POST: {post_title}")
        log.append({
            "item": iid, "cuenta": cuenta,
            "status": "OK" if ok else "POST_MISMATCH",
            "pre_title": pre.get("title"),
            "new_title": new_title,
            "post_title": post_title,
        })
        time.sleep(0.4)

    out = ROOT / "data" / "auditoria" / f"titulos_actualizados_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    out.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    ok_n = sum(1 for x in log if x["status"] == "OK")
    fail_n = sum(1 for x in log if "FAIL" in x["status"] or "MISMATCH" in x["status"])
    skip_n = sum(1 for x in log if "SKIP" in x["status"])
    print(f"\n=== Resumen ===")
    print(f"OK: {ok_n} | FAIL: {fail_n} | SKIP: {skip_n}")
    print(f"LOG: {out}")


if __name__ == "__main__":
    main()
