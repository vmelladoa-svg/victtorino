"""Borra (a la papelera, o permanente con --force) todos los productos de prueba
CL-TEST-* creados por chilat_importar_draft.py. Uso:
  python chilat_borrar_draft.py          # mueve a papelera
  python chilat_borrar_draft.py --force  # borra permanente
"""
import sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"
force = "--force" in sys.argv

# buscar todos los SKU CL-TEST-
r = requests.get(f"{WC}/wp-json/wc/v3/products",
                 params={"consumer_key": KEY, "consumer_secret": SEC,
                         "search": "CL-TEST-", "per_page": 100, "status": "any"}, timeout=30)
prods = [p for p in r.json() if str(p.get("sku", "")).startswith("CL-TEST-")]
print(f"Encontrados {len(prods)} productos de prueba CL-TEST-*")
for p in prods:
    d = requests.delete(f"{WC}/wp-json/wc/v3/products/{p['id']}",
                        params={"consumer_key": KEY, "consumer_secret": SEC,
                                "force": str(force).lower()}, timeout=30)
    print(f"  {'BORRADO' if d.status_code < 300 else 'ERR '+str(d.status_code)}  #{p['id']}  {p.get('name','')[:40]}")
print("Listo." + ("  (permanente)" if force else "  (en papelera; vaciar papelera para eliminar del todo)"))
