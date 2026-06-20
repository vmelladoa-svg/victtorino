import sys, io, requests, re
from urllib.parse import urljoin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0"}

r=requests.get(WC+"/",headers=UA,timeout=40)
html=r.text
print(f"HTML home: {r.status_code}, {len(html)}b\n")

# CSS links
css=re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', html)
css_urls=[]
for c in css:
    m=re.search(r'href=["\']([^"\']+)["\']', c)
    if m: css_urls.append(m.group(1))
js_urls=re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html)

print(f"== {len(css_urls)} CSS, {len(js_urls)} JS encontrados ==\n")

def test(urls, tipo):
    malos=0
    print(f"--- {tipo} ---")
    for u in urls[:25]:
        full=u if u.startswith("http") else urljoin(WC, u)
        # detectar dominio raro (hosting viejo)
        dom=re.search(r'https?://([^/]+)', full)
        dom=dom.group(1) if dom else "?"
        try:
            rr=requests.get(full,headers=UA,timeout=20)
            ct=rr.headers.get("Content-Type","")
            vacio=" VACIO!" if len(rr.content)<5 else ""
            estado="OK" if rr.status_code==200 else "<<< FALLA"
            if rr.status_code!=200 or len(rr.content)<5: malos+=1
            flagdom="" if "victtorino.cl" in dom else f" [DOM:{dom}]"
            print(f"  {rr.status_code} {estado:9s} {len(rr.content):>7d}b {ct[:24]:24s}{vacio}{flagdom}  {u[-70:]}")
        except Exception as e:
            malos+=1
            print(f"  ERR {type(e).__name__}  {u[-70:]}")
    print(f"  >>> {malos} con problema de {min(len(urls),25)}\n")
    return malos

mc=test(css_urls,"CSS")
mj=test(js_urls,"JS")
print(f"RESUMEN: CSS rotos={mc}, JS rotos={mj}")
