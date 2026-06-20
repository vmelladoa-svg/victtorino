"""
Trae atributos completos vía GET /items/{id}?attributes=id,title,attributes
para los TOP 30 items SEO de cero más urgentes.
Output: top30_con_atributos.json
"""
import json
import time
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).parent

TOK = {
    "C1": json.loads((ROOT / "tokens_cuenta1.json").read_text())["access_token"],
    "C2": json.loads((ROOT / "tokens_cuenta2.json").read_text())["access_token"],
    "C3": json.loads((ROOT / "tokens_cuenta3.json").read_text())["access_token"],
}


def main():
    df = pd.read_excel(ROOT / "titulos_sugeridos_seo.xlsx")
    top = df.sort_values(["Urgencia (heredada)", "Score actual"], ascending=[False, True]).head(30)

    out = []
    for _, r in top.iterrows():
        iid = r["ItemID"]
        cuenta = r["Cuenta"]
        h = {"Authorization": f"Bearer {TOK[cuenta]}"}
        rr = requests.get(
            f"https://api.mercadolibre.com/items/{iid}",
            params={"attributes": "id,title,attributes,category_id"},
            headers=h, timeout=15,
        )
        if rr.status_code != 200:
            continue
        it = rr.json()
        attrs = {}
        for a in (it.get("attributes") or []):
            v = a.get("value_name") or ((a.get("values") or [{}])[0].get("name"))
            if v:
                attrs[a["id"]] = v
        out.append({
            "iid": iid,
            "cuenta": cuenta,
            "category_id": it.get("category_id"),
            "title": it.get("title"),
            "attrs": attrs,
            "precio": int(r["Precio"]),
            "stock": int(r["Stock"]),
            "urgencia": int(r["Urgencia (heredada)"]),
        })
        time.sleep(0.1)
    (ROOT / "top30_con_atributos.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(out)} items con atributos guardados")
    # Sample
    for it in out[:3]:
        print(f"\n{it['cuenta']} {it['iid']}: {it['title']}")
        print(f"  Cat: {it['category_id']}, ${it['precio']:,}, stock {it['stock']}")
        print(f"  Attrs ({len(it['attrs'])}): {list(it['attrs'].items())[:8]}")


if __name__ == "__main__":
    main()
