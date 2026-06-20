"""
Fix: visitas en snapshots. El endpoint multi-item /items/visits/time_window
exige un único id por llamada (cause 400). Re-extrae visitas item-por-item
y actualiza data/auditoria/snapshot_*.json sin tocar el resto.
"""
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

ROOT = Path(__file__).parent
OUT = ROOT / "data" / "auditoria"

CUENTAS = [
    ("c1", "tokens_cuenta1.json"),
    ("c2", "tokens_cuenta2.json"),
    ("c3", "tokens_cuenta3.json"),
]
DAYS = 30


def visits_one(token, iid):
    try:
        r = requests.get(
            f"https://api.mercadolibre.com/items/{iid}/visits/time_window",
            headers={"Authorization": f"Bearer {token}"},
            params={"last": DAYS, "unit": "day"},
            timeout=15,
        )
        if r.status_code == 200:
            return iid, r.json().get("total_visits", 0)
    except Exception:
        pass
    return iid, 0


def fix(cuenta, tok_file):
    snap_path = OUT / f"snapshot_{cuenta}.json"
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    token = json.loads(Path(tok_file).read_text())["access_token"]
    ids = snap.get("items_activos", [])
    print(f"\n=== {cuenta.upper()} — {len(ids)} items activos ===")
    visits = {}
    t0 = time.time()
    # 8 threads — la API tolera bien
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(visits_one, token, iid) for iid in ids]
        for i, f in enumerate(as_completed(futs), 1):
            iid, v = f.result()
            visits[iid] = v
            if i % 50 == 0:
                print(f"  {i}/{len(ids)} en {time.time()-t0:.1f}s")
    nz = sum(1 for v in visits.values() if v > 0)
    print(f"  Visitas extraídas: total={sum(visits.values())}, items_con_trafico={nz}, max={max(visits.values()) if visits else 0}")
    snap["visitas_30d"] = visits
    snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Snapshot actualizado: {snap_path}")


if __name__ == "__main__":
    for c, tf in CUENTAS:
        try:
            fix(c, tf)
        except Exception as e:
            print(f"ERROR {c}: {e}")
