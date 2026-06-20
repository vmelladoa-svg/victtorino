import sys, io, requests, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC="https://victtorino.cl"
UA={"User-Agent":"Mozilla/5.0 Chrome/124.0"}
def hash_css(url):
    r=requests.get(url,headers=UA,timeout=30)
    m=re.search(r'/litespeed/css/([0-9a-f]+)\.css', r.text)
    xls=r.headers.get("X-LiteSpeed-Cache","-")
    return (r.status_code, m.group(1)[:12] if m else "NINGUNO", xls)
print("== Confirmar desfase de cache de LiteSpeed ==")
for label,u in [("/ (cache)",WC+"/"),("/ (cache)",WC+"/"),
                ("?nocache A",WC+"/?nc=aa"),("?nocache B",WC+"/?nc=bb"),
                ("/tienda/",WC+"/tienda/"),("/tienda/?nc",WC+"/tienda/?nc=zz")]:
    st,h,xls=hash_css(u)
    # probar si ese css existe
    full=f"{WC}/wp-content/litespeed/css/{h}.css" if h not in("NINGUNO",) else None
    css_st="-"
    if full:
        css_st=requests.get(full,headers=UA,timeout=15).status_code
    print(f"  {label:14s} html={st} css_hash={h:13s} css_http={css_st}  X-LiteSpeed={xls}")
