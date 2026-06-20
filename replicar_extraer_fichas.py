"""
Extrae ficha completa (título, descripción, atributos, fotos) de los items
ganadores y perdedores del plan top 15. Guarda raw_fichas.json.
"""
import json
import time
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).parent
PLAN_FILE = ROOT / "plan_replicacion_top15.xlsx"
OUT_FILE = ROOT / "data" / "auditoria" / "raw_fichas.json"

TOKENS = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}


def get_item(cuenta, item_id):
    token = TOKENS[cuenta]
    h = {"Authorization": f"Bearer {token}"}
    # Item base
    r = requests.get(f"https://api.mercadolibre.com/items/{item_id}", headers=h, timeout=15)
    if r.status_code != 200:
        return {"error": r.status_code, "body": r.text[:200]}
    it = r.json()
    # Descripción (endpoint separado)
    rd = requests.get(f"https://api.mercadolibre.com/items/{item_id}/description", headers=h, timeout=15)
    desc = rd.json() if rd.status_code == 200 else {}
    it["_description"] = desc
    return it


def main():
    plan = pd.read_excel(PLAN_FILE)
    print(f"Plan: {len(plan)} pares")

    # Conjunto único de items
    ids = set()
    for _, r in plan.iterrows():
        ids.add((r["Win_Cuenta"], r["Win_ID"]))
        ids.add((r["Lose_Cuenta"], r["Lose_ID"]))
    print(f"Items únicos a traer: {len(ids)}")

    fichas = {}
    for i, (cuenta, iid) in enumerate(sorted(ids), 1):
        print(f"  [{i}/{len(ids)}] {cuenta} {iid}")
        fichas[iid] = get_item(cuenta, iid)
        time.sleep(0.1)

    OUT_FILE.write_text(json.dumps(fichas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {OUT_FILE} ({OUT_FILE.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
