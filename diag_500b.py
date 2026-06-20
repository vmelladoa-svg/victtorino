import sys, io, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
P={"consumer_key":"ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
   "consumer_secret":"cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
UA={"User-Agent":"Mozilla/5.0"}

print("== 1) ¿Sigue el 500 ahora? ==")
for ep in ["/wp-json/wc/v3","/wp-json/wc/v3/products?per_page=1"]:
    r=requests.get(WC+ep,params=P,headers=UA,timeout=40)
    print(f"   {r.status_code}  {ep}")
    # ¿el body trae algún rastro? buscar el header X-* o un id de error
    for h in ["CF-Ray","X-Litespeed-Cache"]:
        if h in r.headers: print(f"      {h}: {r.headers[h]}")

print("\n== 2) ¿debug.log accesible por web? ==")
for ruta in ["/wp-content/debug.log","/wp-content/uploads/debug.log","/error_log","/wp-content/error_log"]:
    try:
        r=requests.get(WC+ruta,headers=UA,timeout=20)
        print(f"   {r.status_code} {len(r.content)}b  {ruta}")
        if r.status_code==200 and len(r.content)>0:
            # ultimas lineas con 'Fatal' o '.php'
            txt=r.text
            for m in re.findall(r"PHP (Fatal|Parse|Warning).{0,260}", txt)[-8:]:
                print("      >>",m.strip())
    except Exception as e:
        print(f"   ERR {ruta}: {e}")

print("\n== 3) Versión WC y db_version vía Store API / front ==")
# La Store API no da version, pero el readme via uploads a veces sí. Probar el endpoint de estado público
for ep in ["/wp-json/wc/store/v1/products?per_page=1"]:
    r=requests.get(WC+ep,headers=UA,timeout=30)
    print(f"   store products: {r.status_code}")
    # cabecera de versión a veces
    for h in r.headers:
        if "woo" in h.lower() or "version" in h.lower():
            print(f"      {h}: {r.headers[h]}")

print("\n== 4) ¿La home declara WC y su versión en assets? ==")
r=requests.get(WC+"/tienda/",headers=UA,timeout=30)
for m in set(re.findall(r"woocommerce[^\"']*?ver=([\d.]+)", r.text)):
    print(f"   asset woocommerce ver={m}")
for m in set(re.findall(r"/woocommerce(?:-blocks)?/[^\"']*?ver=([\d.]+)", r.text)):
    print(f"   wc-blocks ver={m}")
