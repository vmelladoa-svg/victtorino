"""
Auto-completa fotos cross-cuenta usando snapshots locales.
Estrategia:
  - Para cada item activo con <4 fotos
  - Buscar mismo SKU/título normalizado en otras 2 cuentas
  - Tomar la fuente con MÁS fotos (siempre >= fotos actuales del target)
  - Dry-run muestra plan; --execute aplica vía PUT /items/{id}

Mejoras respecto a mejorar_fotos_c1_c3.py:
  - Cubre C1, C2 y C3 (no solo C1+C3)
  - Match por SKU o por título normalizado (no solo SKU)
  - Dry-run por defecto
  - Lee snapshots locales (no re-llama API)
"""
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
import requests
import pickle

ROOT = Path(__file__).parent
ANALISIS = ROOT / "data" / "auditoria" / "analisis.pkl"

TOK = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}

MIN_FOTOS_OBJETIVO = 4  # umbral mínimo deseado
MIN_GANANCIA = 1        # mejorar solo si la fuente tiene al menos +1 foto


def normalize(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def build_index(snapshots):
    """Devuelve dict por cuenta con metadata + indices SKU/título."""
    by_cuenta = {}
    for c in ("C1", "C2", "C3"):
        items = []
        for it in snapshots[c]["items"]:
            if it.get("status") != "active":
                continue
            sku_raw = (it.get("seller_custom_field") or "").strip().upper()
            pics = [p["url"] for p in (it.get("pictures") or [])]
            items.append({
                "id": it["id"], "title": it.get("title") or "",
                "norm": normalize(it.get("title")),
                "sku": sku_raw,
                "pics": pics, "n_pics": len(pics),
            })
        by_cuenta[c] = items
    # indices
    sku_idx = {}; title_idx = {}
    for c, lst in by_cuenta.items():
        for it in lst:
            it["_cuenta"] = c
            if it["sku"]:
                sku_idx.setdefault(it["sku"], []).append(it)
            if it["norm"]:
                title_idx.setdefault(it["norm"], []).append(it)
    return by_cuenta, sku_idx, title_idx


def find_best_source(target, sku_idx, title_idx):
    """Devuelve la mejor fuente alternativa (más fotos) o None."""
    candidates = []
    if target["sku"]:
        candidates.extend(sku_idx.get(target["sku"], []))
    candidates.extend(title_idx.get(target["norm"], []))
    # dedup por ID
    seen = set()
    best = None
    for c in candidates:
        if c["id"] == target["id"] or c["id"] in seen:
            continue
        seen.add(c["id"])
        if c["n_pics"] >= target["n_pics"] + MIN_GANANCIA:
            if best is None or c["n_pics"] > best["n_pics"]:
                best = c
    return best


def build_plan(by_cuenta, sku_idx, title_idx):
    plan = []
    for cuenta, items in by_cuenta.items():
        for t in items:
            if t["n_pics"] >= MIN_FOTOS_OBJETIVO:
                continue
            src = find_best_source(t, sku_idx, title_idx)
            if not src:
                continue
            plan.append({
                "target_cuenta": cuenta, "target_id": t["id"],
                "target_title": t["title"], "target_sku": t["sku"],
                "target_n_pics": t["n_pics"],
                "src_cuenta": src["_cuenta"], "src_id": src["id"],
                "src_n_pics": src["n_pics"],
                "src_pics": src["pics"],
            })
    return plan


def main(execute=False):
    data = pickle.loads(ANALISIS.read_bytes())
    snapshots = data["snapshots"]
    by_cuenta, sku_idx, title_idx = build_index(snapshots)
    plan = build_plan(by_cuenta, sku_idx, title_idx)
    print(f"Items target (<{MIN_FOTOS_OBJETIVO} fotos con fuente disponible): {len(plan)}")
    # Resumen por cuenta
    from collections import Counter
    c = Counter(p["target_cuenta"] for p in plan)
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")

    if not plan:
        return

    print(f"\n=== Plan ({('EJECUTANDO' if execute else 'DRY-RUN')}) ===\n")
    log = []
    for i, p in enumerate(plan, 1):
        print(f"[{i:3d}/{len(plan)}] {p['target_cuenta']} {p['target_id']} ({p['target_n_pics']}p) "
              f"← {p['src_cuenta']} {p['src_id']} ({p['src_n_pics']}p)  | {p['target_title'][:50]}")

        if not execute:
            log.append({**{k: v for k, v in p.items() if k != "src_pics"}, "status": "DRY_RUN"})
            continue

        h = {"Authorization": f"Bearer {TOK[p['target_cuenta']]}", "Content-Type": "application/json"}
        # PUT con pictures como source URLs (https)
        pics_payload = [{"source": u.replace("http://", "https://")} for u in p["src_pics"]]
        r = requests.put(
            f"https://api.mercadolibre.com/items/{p['target_id']}",
            headers=h, json={"pictures": pics_payload}, timeout=30,
        )
        if r.status_code == 200:
            print(f"          ✓ OK")
            log.append({**{k: v for k, v in p.items() if k != "src_pics"}, "status": "OK"})
        else:
            try:
                err = r.json()
            except Exception:
                err = r.text[:200]
            print(f"          ✗ {r.status_code} {err}")
            log.append({**{k: v for k, v in p.items() if k != "src_pics"}, "status": "FAIL",
                       "http": r.status_code, "detail": str(err)[:300]})
        time.sleep(0.4)

    if execute:
        out = ROOT / "data" / "auditoria" / f"fotos_cross_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        out.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
        ok = sum(1 for x in log if x["status"] == "OK")
        fail = sum(1 for x in log if x["status"] == "FAIL")
        print(f"\nOK: {ok} | FAIL: {fail}")
        print(f"LOG: {out}")


if __name__ == "__main__":
    main(execute=("--execute" in sys.argv))
