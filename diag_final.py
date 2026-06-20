import sys, io, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 Chrome/124.0"}

print("== 1) Re-test del CSS que ANTES dio 200, exacto y variantes ==")
urls=[
 "/wp-content/litespeed/css/e08a0b7fbd6673b4758e977210ba01d2.css?ver=a37b3",
 "/wp-content/litespeed/css/e08a0b7fbd6673b4758e977210ba01d2.css",
]
for u in urls:
    r=requests.get(WC+u,headers=UA,timeout=20)
    es404wp = "Página WP 404" if r.status_code==404 else ""
    print(f"  {r.status_code} {len(r.content):>7d}b  {es404wp}  {u[-55:]}")

print("\n== 2) ¿El directorio /wp-content/litespeed/ existe y es navegable? ==")
for u in ["/wp-content/litespeed/","/wp-content/litespeed/css/","/wp-content/cache/"]:
    r=requests.get(WC+u,headers=UA,timeout=15)
    print(f"  {r.status_code} {len(r.content):>6d}b  {u}")

print("\n== 3) Pedir la MISMA home 5 veces seguidas: ¿el css llega a existir alguna vez? ==")
import time
for i in range(5):
    r=requests.get(WC+f"/?probe={i}",headers=UA,timeout=30)
    m=re.search(r'/litespeed/css/([0-9a-f]+)\.css(\?ver=[0-9a-f]+)?',r.text)
    if m:
        path=m.group(0)
        css=requests.get(WC+"/wp-content"+path if not path.startswith("/wp-content") else WC+path,headers=UA,timeout=15)
        # construir bien
        full=WC+(path if path.startswith("/wp-content") else "/wp-content"+path)
        css=requests.get(full,headers=UA,timeout=15)
        print(f"  intento {i}: hash={m.group(1)[:10]} -> css HTTP {css.status_code} ({len(css.content)}b)")
    time.sleep(1)

print("\n== 4) ¿Hay CSS NO-litespeed (individuales) como fallback? (inline styles?) ==")
r=requests.get(WC+"/",headers=UA,timeout=30)
inline=len(re.findall(r'<style', r.text))
print(f"  bloques <style> inline en home: {inline}")
