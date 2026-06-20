"""Diagnóstico de imágenes del sitio: peso, formato, oportunidad de optimización."""
import sys, io, requests, re
from collections import defaultdict
from urllib.parse import urlparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}


def tamaño_imagen(url, timeout=10):
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return int(r.headers.get("Content-Length", 0))
    except Exception:
        pass
    return 0


# 1) Sample de productos para extraer imágenes (no todos los 286)
print("[1/3] Cargando 30 productos para análisis...")
import random
random.seed(42)

# Get product IDs (no quiero recorrer paginación, uso WC API directo y solo tomo sample)
r = requests.get(f"{WC}/wp-json/wc/v3/products",
                 params={**P, "per_page": 50, "status": "publish"}, timeout=60)
productos = r.json()

# Recopilar URLs de imágenes únicas
imagenes_urls = set()
for p in productos[:30]:
    for img in p.get("images", []):
        if img.get("src"):
            imagenes_urls.add(img["src"])

# Imágenes del header/home
home_html = requests.get(WC, timeout=30).text
hero_imgs = re.findall(r'src="(https://victtorino\.cl/wp-content/uploads/[^"]+\.(?:jpg|jpeg|png|webp))"', home_html)
hero_imgs += re.findall(r'data-src="(https://victtorino\.cl/wp-content/uploads/[^"]+\.(?:jpg|jpeg|png|webp))"', home_html)
for u in hero_imgs[:20]:
    imagenes_urls.add(u)

print(f"      {len(imagenes_urls)} imágenes únicas a analizar")

# 2) Medir cada una
print("\n[2/3] Midiendo tamaños...")
resultados = []
for url in imagenes_urls:
    size = tamaño_imagen(url)
    if size > 0:
        ext = url.rsplit(".", 1)[-1].lower()
        resultados.append({"url": url, "size": size, "ext": ext})

# Stats
from collections import Counter
total_bytes = sum(r["size"] for r in resultados)
formato_count = Counter(r["ext"] for r in resultados)
formato_bytes = defaultdict(int)
for r in resultados:
    formato_bytes[r["ext"]] += r["size"]

# 3) Reporte
print(f"\n[3/3] Análisis\n")
print("=" * 80)
print(f"RESUMEN — {len(resultados)} imágenes analizadas, {total_bytes/1024:.0f} KB totales")
print("=" * 80)
print(f"\nDistribución por formato:")
for ext, count in formato_count.most_common():
    pct_count = count * 100 // len(resultados)
    bytes_total = formato_bytes[ext]
    pct_bytes = bytes_total * 100 // total_bytes if total_bytes else 0
    print(f"  .{ext:5} {count:3} imágenes ({pct_count:2}%)  -  {bytes_total/1024:6.0f} KB ({pct_bytes:2}% del peso)")

# Top 10 más pesadas
print(f"\nTop 15 imágenes más pesadas:")
resultados.sort(key=lambda x: -x["size"])
for r in resultados[:15]:
    flag = "🔴" if r["size"] > 100000 else "🟡" if r["size"] > 50000 else "🟢"
    nombre = r["url"].rsplit("/", 1)[-1]
    print(f"  {flag} {r['size']/1024:6.0f} KB  .{r['ext']:4}  {nombre[:60]}")

# Estimación de ahorro
ahorro_potencial = 0
for r in resultados:
    if r["ext"] in ("jpg", "jpeg", "png"):
        # WebP típicamente 30-50% menos peso
        ahorro_potencial += r["size"] * 0.4
    elif r["ext"] == "webp":
        # WebP ya optimizado puede tener 10-15% más reducción
        ahorro_potencial += r["size"] * 0.1

print(f"\n=== POTENCIAL DE OPTIMIZACIÓN ===")
print(f"  Peso actual estimado catálogo:  {total_bytes/1024:.0f} KB")
print(f"  Ahorro estimado con optimización: {ahorro_potencial/1024:.0f} KB ({ahorro_potencial*100/total_bytes if total_bytes else 0:.0f}%)")
print(f"  Peso después:                    {(total_bytes-ahorro_potencial)/1024:.0f} KB")
