"""
Sube a WooCommerce las fotos de ML para productos web SIN imagen.
Lee plan_fotos_web.json (clave 'seguro' por defecto) y hace PUT de las
URLs de mlstatic.com como images[] -> WC las descarga y crea attachments.

Uso:
  python aplicar_fotos_web.py            # aplica los 'seguro'
  python aplicar_fotos_web.py 1829 1821  # aplica woo_ids puntuales (busca en seguro+dudoso)
"""
import json, sys, io, requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

plan = json.load(open("plan_fotos_web.json", encoding="utf-8"))
pool = {str(r["woo_id"]): r for r in plan["seguro"] + plan["dudoso"]}

args = sys.argv[1:]
if args:
    objetivos = [pool[a] for a in args if a in pool]
else:
    objetivos = plan["seguro"]

print(f"Productos a procesar: {len(objetivos)}\n")
resultados = []
for r in objetivos:
    wid = r["woo_id"]
    urls = r["urls"]
    # verificar que sigue sin imagen
    g = requests.get(f"{WC}/wp-json/wc/v3/products/{wid}",
                     params={"consumer_key": KEY, "consumer_secret": SEC}, timeout=30)
    if g.status_code >= 400:
        print(f"  [{wid}] ERROR GET {g.status_code}"); continue
    prod = g.json()
    if prod.get("images"):
        print(f"  [{wid}] YA tiene {len(prod['images'])} imagen(es) -> salto");
        resultados.append({"woo_id": wid, "estado": "ya_tenia"}); continue

    images = [{"src": u, "position": i} for i, u in enumerate(urls)]
    p = requests.put(f"{WC}/wp-json/wc/v3/products/{wid}",
                     params={"consumer_key": KEY, "consumer_secret": SEC},
                     json={"images": images}, timeout=180)
    if p.status_code >= 400:
        print(f"  [{wid}] ERROR PUT {p.status_code}: {p.text[:200]}")
        resultados.append({"woo_id": wid, "estado": "error", "detalle": p.text[:200]}); continue
    fin = p.json().get("images", [])
    print(f"  [{wid}] OK  {len(urls)} enviadas -> {len(fin)} en web  | {r['name'][:45]}")
    resultados.append({"woo_id": wid, "estado": "ok", "subidas": len(fin),
                       "ml_id": r["ml_id"], "ml_cuenta": r["ml_cuenta"]})

ok = sum(1 for x in resultados if x["estado"] == "ok")
print(f"\n=== {ok}/{len(objetivos)} actualizados con fotos ===")
json.dump(resultados, open("aplicar_fotos_web_resultado.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
