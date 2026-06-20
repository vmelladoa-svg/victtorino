"""Aplica fotos ML a los productos web aprobados (plan_aprobados.json).
Preserva imagenes existentes (por id) y agrega las nuevas de mlstatic."""
import json, sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
WC="https://victtorino.cl";K="ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15";S="cs_3604e7ebdb8ff78442731344cc95af50516188a5"
plan=json.load(open("plan_aprobados.json",encoding="utf-8"))
res=[]
for r in plan:
    wid=r["woo_id"]
    images=[{"id":i} for i in r["existentes"]]+[{"src":u} for u in r["urls"]]
    p=requests.put(f"{WC}/wp-json/wc/v3/products/{wid}",
                   params={"consumer_key":K,"consumer_secret":S},
                   json={"images":images},timeout=180)
    if p.status_code>=400:
        print(f"  [{wid}] ERROR {p.status_code}: {p.text[:120]}")
        res.append({"woo_id":wid,"estado":f"error_{p.status_code}"});continue
    fin=p.json().get("images",[])
    print(f"  [{wid}] OK  {len(r['existentes'])} previas + {len(r['urls'])} ML -> {len(fin)} en web | {r['name'][:40]}")
    res.append({"woo_id":wid,"estado":"ok","total":len(fin)})
ok=sum(1 for x in res if x["estado"]=="ok")
print(f"\n=== {ok}/{len(plan)} OK ===")
json.dump(res,open("aplicar_aprobados_resultado.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
