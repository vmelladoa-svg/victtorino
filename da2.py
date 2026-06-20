import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
html=open(r'C:\Users\dell\victtorino\dom.html',encoding='utf-8',errors='ignore').read()
# Buscar imgs con vtr-img o wp-image (las de producto)
print("=== <img> de producto (vtr-img-primary/secondary o wp-image) ===")
imgs=re.findall(r'<img[^>]*(?:vtr-img|wp-image-\d)[^>]*>', html)
print(f"  encontradas: {len(imgs)}")
for m in imgs[:4]:
    print("   "+m[:300])
    print()
print("=== ¿vtr-hover-wrap en el DOM? (el JS lo crea) ===")
print(f"  vtr-hover-wrap: {html.count('vtr-hover-wrap')}")
print(f"  vtr-img-primary: {html.count('vtr-img-primary')}")
print(f"  vtr-img-secondary: {html.count('vtr-img-secondary')}")
# un loop item completo de imagen
print("\n=== primer <a> dentro de un widget featured-image (con su img) ===")
for m in re.finditer(r'elementor-widget-theme-post-featured-image', html):
    seg=html[m.start():m.start()+700]
    a=re.search(r'<a\b.*?</a>', seg, re.S)
    if a:
        print(re.sub(r'>\s*<','>\n<',a.group(0)[:600]))
        break
