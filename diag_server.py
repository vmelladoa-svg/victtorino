import sys, io, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 Chrome/124.0"}
print("== Headers del 500 de WC REST (¿filtra PHP/servidor?) ==")
r=requests.get(WC+"/wp-json/wc/v3/products?per_page=1",
   params={"consumer_key":"ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
           "consumer_secret":"cs_3604e7ebdb8ff78442731344cc95af50516188a5"},
   headers=UA,timeout=40)
for h in ["Server","X-Powered-By","X-Php-Version","Platform","X-Server","Via"]:
    if h in r.headers: print(f"   {h}: {r.headers[h]}")
print(f"   (status {r.status_code})")
print("\n== ¿debug.log existe? (403=sí, protegido / 404=no) ==")
for u in ["/wp-content/debug.log","/wp-content/uploads/debug.log"]:
    rr=requests.get(WC+u,headers=UA,timeout=15)
    print(f"   {rr.status_code}  {u}")
print("\n== ¿wp-content/plugins listable o protegido? ==")
rr=requests.get(WC+"/wp-content/plugins/",headers=UA,timeout=15)
print(f"   {rr.status_code}  /wp-content/plugins/")
