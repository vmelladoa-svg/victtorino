"""Lista los 77 productos del Lote A con id, titulo, categoria principal."""
import json, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
with open(r"C:\Users\dell\victtorino\analisis_seo_huerfanos.json", encoding="utf-8") as f:
    data = json.load(f)
ids = data["sin_focus_desc_decente"]
print(f"Total: {len(ids)}\n")
salida = []
for pid in ids:
    r = requests.get(f"https://victtorino.cl/wp-json/wc/v3/products/{pid}", params=P, timeout=30).json()
    cat = (r.get("categories") or [{"name": "(sin)"}])[0]["name"]
    salida.append({"id": pid, "name": r.get("name", ""), "cat": cat})
    print(f"{pid:5} [{cat[:20]:20}] {r.get('name','')[:60]}")
with open(r"C:\Users\dell\victtorino\lote_a_listado.json", "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)
print(f"\nGuardado en lote_a_listado.json")
