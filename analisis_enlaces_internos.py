"""
Análisis de enlaces internos en victtorino.cl.

Estrategia (sin Screaming Frog):
1. Listar todas las URLs del sitemap (productos + categorías + páginas).
2. Bajar el HTML de las páginas "hub" (home + 10 categorías + pages clave).
3. Extraer enlaces internos (href apuntando a victtorino.cl).
4. Construir grafo simple: destino -> [orígenes que lo enlazan].
5. Detectar:
   - Productos huérfanos (sin enlaces internos)
   - Productos con anchor text genérico
   - Páginas con muchos enlaces (over-linked)
   - Categorías huérfanas
"""
import json
import sys
import io
import re
import time
import requests
from collections import Counter, defaultdict
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
DOMAIN = "victtorino.cl"

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def fetch(url, timeout=30):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 SEOAudit"})
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None


def parse_sitemap_index(xml):
    """Parsea un sitemap index y devuelve URLs de subsitemaps."""
    root = ET.fromstring(xml)
    return [loc.text for loc in root.findall(".//sm:loc", NS)]


def parse_urls_sitemap(xml):
    """Parsea un urlset y devuelve las URLs."""
    root = ET.fromstring(xml)
    return [loc.text for loc in root.findall(".//sm:loc", NS)]


# 1) Listar todas las URLs del sitemap
print("[1/4] Recopilando URLs del sitemap...")
idx_xml = fetch(f"{WC}/sitemap_index.xml")
subsitemaps = parse_sitemap_index(idx_xml)
print(f"      subsitemaps: {len(subsitemaps)}")
todas_urls = set()
for sm in subsitemaps:
    xml = fetch(sm)
    if xml:
        urls = parse_urls_sitemap(xml)
        todas_urls.update(urls)
        print(f"      {sm.split('/')[-1]}: {len(urls)} URLs")
print(f"      Total URLs en sitemap: {len(todas_urls)}")

# 2) Bajar HTML de "hubs" (home, categorías, pages clave)
print("\n[2/4] Bajando HTML de las páginas hub...")
hub_urls = [WC + "/"]
# Categorías
for u in todas_urls:
    if "/product-category/" in u:
        hub_urls.append(u)
# Pages no-producto
for u in todas_urls:
    if "/producto/" not in u and "/product-category/" not in u and u not in hub_urls:
        hub_urls.append(u)
hub_urls = list(set(hub_urls))
print(f"      hubs identificados: {len(hub_urls)}")

# Bajar también algunos productos al azar (sampling) para ver si productos enlazan entre sí
producto_urls = [u for u in todas_urls if "/producto/" in u]
import random
random.seed(42)
sample_productos = random.sample(producto_urls, min(30, len(producto_urls)))
print(f"      sample de productos: {len(sample_productos)}")

all_to_fetch = hub_urls + sample_productos
print(f"      total a bajar: {len(all_to_fetch)} páginas")

html_por_url = {}
for i, url in enumerate(all_to_fetch, start=1):
    html = fetch(url)
    if html:
        html_por_url[url] = html
    if i % 10 == 0:
        print(f"        bajadas {i}/{len(all_to_fetch)}")
    time.sleep(0.3)  # no saturar
print(f"      OK: {len(html_por_url)} páginas bajadas")

# 3) Extraer enlaces internos
print("\n[3/4] Extrayendo enlaces internos...")
# patrón: href="URL_VICTTORINO" anchor texto inside <a>
LINK_RE = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)

def es_interno(href):
    if href.startswith("/"):
        return True
    if href.startswith(WC):
        return True
    if "//" + DOMAIN in href:
        return True
    return False

def normalizar_url(href, base):
    href = urljoin(base, href)
    # quitar query strings y fragments
    p = urlparse(href)
    path = p.path
    if not path.endswith("/") and not path.split("/")[-1].count("."):
        path += "/"
    return f"https://{p.netloc}{path}"

def clean_anchor(txt):
    # quitar tags HTML
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:100]

# Grafo: destino -> [(origen, anchor)]
grafo_in = defaultdict(list)
# Por origen -> total links salientes
grafo_out = defaultdict(int)

for src_url, html in html_por_url.items():
    for m in LINK_RE.finditer(html):
        href, raw_anchor = m.group(1), m.group(2)
        if not es_interno(href):
            continue
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        try:
            target = normalizar_url(href, src_url)
        except Exception:
            continue
        # filtrar enlaces a archivos no HTML
        if any(target.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".svg", ".pdf", ".webp", ".css", ".js", ".xml")):
            continue
        # auto-link?
        if target.rstrip("/") == src_url.rstrip("/"):
            continue
        anchor = clean_anchor(raw_anchor)
        grafo_in[target].append((src_url, anchor))
        grafo_out[src_url] += 1

# 4) Reporte
print("\n[4/4] Generando reporte...")

# Normalizar URLs del sitemap
sitemap_norm = set()
for u in todas_urls:
    p = urlparse(u)
    path = p.path if p.path.endswith("/") else p.path + "/"
    sitemap_norm.add(f"https://{p.netloc}{path}")

# Productos huérfanos: en sitemap, en /producto/, pero NO en grafo_in (o solo 1 link entrante)
productos_en_sitemap = [u for u in sitemap_norm if "/producto/" in u]
huerfanos = []
debiles = []  # 1-2 links
for u in productos_en_sitemap:
    enlaces = grafo_in.get(u, [])
    if not enlaces:
        huerfanos.append(u)
    elif len(enlaces) <= 2:
        debiles.append((u, len(enlaces)))

# Categorías huérfanas
cats_en_sitemap = [u for u in sitemap_norm if "/product-category/" in u]
cats_huerfanas = []
cats_links = {}
for u in cats_en_sitemap:
    enlaces = grafo_in.get(u, [])
    cats_links[u] = len(enlaces)
    if not enlaces:
        cats_huerfanas.append(u)

# Anchor text genérico (links a productos)
GENERIC_ANCHORS = {"ver más", "ver mas", "más info", "mas info", "click", "click aquí",
                   "click aqui", "leer más", "leer mas", "ver", "aquí", "aqui",
                   "details", "ver detalles", "comprar", "compra", "add", "añadir"}

anchor_generico = 0
anchor_descriptivo = 0
anchor_solo_imagen = 0
for u, enlaces in grafo_in.items():
    if "/producto/" not in u:
        continue
    for src, anchor in enlaces:
        if not anchor:
            anchor_solo_imagen += 1
        elif anchor.lower().strip() in GENERIC_ANCHORS or len(anchor) < 4:
            anchor_generico += 1
        else:
            anchor_descriptivo += 1

# Páginas con muchos links salientes
top_out = sorted(grafo_out.items(), key=lambda x: -x[1])[:10]

# Reporte
print("\n" + "=" * 80)
print(f"ANÁLISIS DE ENLACES INTERNOS — victtorino.cl")
print("=" * 80)

print(f"\n## RESUMEN")
print(f"  URLs en sitemap:           {len(todas_urls)}")
print(f"    productos:               {len(productos_en_sitemap)}")
print(f"    categorías:              {len(cats_en_sitemap)}")
print(f"  Páginas crawleadas:        {len(html_por_url)}")
print(f"  Enlaces internos detectados: {sum(len(v) for v in grafo_in.values())}")
print(f"  URLs únicas que reciben links: {len(grafo_in)}")

print(f"\n## CRÍTICO — Productos HUÉRFANOS (cero enlaces internos desde hubs)")
print(f"  Total: {len(huerfanos)} de {len(productos_en_sitemap)} ({len(huerfanos)*100//max(len(productos_en_sitemap),1)}%)")
print(f"  Primeros 20:")
for u in huerfanos[:20]:
    print(f"    {u}")

print(f"\n## ALTO — Productos DÉBILES (solo 1-2 enlaces internos)")
print(f"  Total: {len(debiles)}")
debiles_sorted = sorted(debiles, key=lambda x: x[1])
for u, n in debiles_sorted[:15]:
    print(f"    {n}  {u}")

print(f"\n## CATEGORÍAS — enlaces entrantes")
for u in sorted(cats_en_sitemap):
    n = cats_links.get(u, 0)
    flag = " <-- huérfana!" if n == 0 else ""
    print(f"  {n:3}  {u.replace(WC, '')}{flag}")

print(f"\n## ANCHOR TEXT — distribución en links a productos")
total_a = anchor_generico + anchor_descriptivo + anchor_solo_imagen
if total_a:
    print(f"  Solo imagen (sin texto):  {anchor_solo_imagen:5}  ({anchor_solo_imagen*100//total_a}%)")
    print(f"  Genérico:                 {anchor_generico:5}  ({anchor_generico*100//total_a}%)")
    print(f"  Descriptivo (ideal):      {anchor_descriptivo:5}  ({anchor_descriptivo*100//total_a}%)")

print(f"\n## TOP 10 páginas con más links salientes (posibles 'hub' o over-linked)")
for url, n in top_out:
    print(f"  {n:4}  {url}")

# Detección de broken links (sample): verificar 20 random destinations
print(f"\n## BROKEN LINKS — verificación (sample de 30 enlaces salientes)")
all_links_out = []
for src, html in html_por_url.items():
    for m in LINK_RE.finditer(html):
        href = m.group(1)
        if not es_interno(href) or href.startswith("#"):
            continue
        try:
            target = normalizar_url(href, src)
        except Exception:
            continue
        if any(target.endswith(ext) for ext in (".jpg", ".png", ".css", ".js", ".xml")):
            continue
        all_links_out.append((src, target))

unicos = list(set(t for _, t in all_links_out))
sample_check = random.sample(unicos, min(30, len(unicos)))
broken = []
for url in sample_check:
    try:
        r = requests.head(url, allow_redirects=False, timeout=10)
        if r.status_code >= 400:
            broken.append((url, r.status_code))
    except Exception:
        broken.append((url, "TIMEOUT"))
if broken:
    print(f"  Encontrados {len(broken)} con problema (de {len(sample_check)} verificados):")
    for u, code in broken[:10]:
        print(f"    {code}  {u}")
else:
    print(f"  Sin broken links en el sample ({len(sample_check)} verificados)")

# Guardar
with open(r"C:\Users\dell\victtorino\enlaces_internos_resultado.json", "w", encoding="utf-8") as f:
    json.dump({
        "urls_sitemap": len(todas_urls),
        "productos_huerfanos": huerfanos,
        "productos_debiles": [{"url": u, "links": n} for u, n in debiles],
        "categorias_links": {u.replace(WC, ""): n for u, n in cats_links.items()},
        "anchor_stats": {
            "solo_imagen": anchor_solo_imagen,
            "generico": anchor_generico,
            "descriptivo": anchor_descriptivo,
        },
        "broken_sample": [{"url": u, "code": str(c)} for u, c in broken],
    }, f, ensure_ascii=False, indent=2)
print(f"\nDetalle guardado en enlaces_internos_resultado.json")
