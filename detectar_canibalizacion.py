"""
Detección de canibalización en victtorino.cl sin GSC.

Estrategia:
- Trae todos los productos publicados de Woo (con title, slug, focus_keyword).
- Normaliza títulos sacando ruido comercial.
- Agrupa por similitud (Jaccard sobre tokens significativos).
- Para cada grupo de 2+ productos, calcula severity y propone acción.
- También revisa focus_keyword duplicados (señal directa de canibalización).
"""
import json
import sys
import io
import re
import unicodedata
import requests
from collections import defaultdict, Counter
from itertools import combinations

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}


def normalizar(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    ruido = {"envio", "gratis", "nuevo", "oferta", "promo", "stock", "ml", "mlc",
             "victtorino", "victorino", "chile", "para", "con", "sin", "de", "del",
             "la", "el", "los", "las", "un", "una", "y", "o", "en", "x"}
    return [t for t in s.split() if t and t not in ruido and len(t) > 1]


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# 1) Cargar todos los productos publish
print("[1/4] Cargando todos los productos publicados...")
productos = []
page = 1
while True:
    r = requests.get(f"{WC}/wp-json/wc/v3/products",
                     params={**P, "per_page": 100, "page": page, "status": "publish"},
                     timeout=30)
    if r.status_code != 200:
        break
    d = r.json()
    if not d:
        break
    for p in d:
        meta = {m["key"]: m["value"] for m in p.get("meta_data", []) if "rank_math" in m["key"]}
        productos.append({
            "id": p["id"],
            "name": p["name"],
            "slug": p["slug"],
            "tokens": normalizar(p["name"]),
            "focus": meta.get("rank_math_focus_keyword", ""),
            "cats": [c["name"] for c in p.get("categories", [])],
            "url": p.get("permalink", ""),
        })
    if int(r.headers.get("X-WP-TotalPages", 1)) <= page:
        break
    page += 1
print(f"      total: {len(productos)} productos publicados")

# 2) Detectar canibalización por SIMILITUD DE TITULO (jaccard >= 0.6)
print("\n[2/4] Detectando overlaps de título (jaccard >= 0.6)...")
overlaps = []
for a, b in combinations(productos, 2):
    if not a["tokens"] or not b["tokens"]:
        continue
    j = jaccard(a["tokens"], b["tokens"])
    if j >= 0.6:
        overlaps.append((j, a, b))
overlaps.sort(key=lambda x: -x[0])
print(f"      overlaps detectados: {len(overlaps)}")

# 3) Detectar canibalización por FOCUS KEYWORD DUPLICADO
print("\n[3/4] Detectando focus keyword duplicados...")
por_focus = defaultdict(list)
for p in productos:
    if p["focus"]:
        por_focus[p["focus"].lower().strip()].append(p)
focus_dup = {k: v for k, v in por_focus.items() if len(v) >= 2}
print(f"      focus keywords con 2+ productos: {len(focus_dup)}")
for fk, lista in sorted(focus_dup.items(), key=lambda x: -len(x[1])):
    print(f"        \"{fk}\" -> {len(lista)} productos")

# 4) Severity + acciones
print("\n[4/4] Calculando severity y acciones por caso...")

# Agrupar overlaps por "cluster" (productos conectados por similitud)
# Approach simple: usar union-find
parent = {p["id"]: p["id"] for p in productos}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(x, y):
    px, py = find(x), find(y)
    if px != py:
        parent[px] = py

for j, a, b in overlaps:
    union(a["id"], b["id"])

clusters = defaultdict(list)
for p in productos:
    root = find(p["id"])
    clusters[root].append(p)
clusters_canibal = {root: lista for root, lista in clusters.items() if len(lista) >= 2}
print(f"      clusters de canibalización: {len(clusters_canibal)}")

# Reporte
print("\n" + "=" * 90)
print(f"REPORTE DE CANIBALIZACIÓN — victtorino.cl ({len(productos)} productos analizados)")
print("=" * 90)

print(f"\n## Focus keyword duplicados (canibalización CONFIRMADA — 2+ productos apuntan a la misma keyword)\n")
focus_canibal = []
for fk, lista in sorted(focus_dup.items(), key=lambda x: -len(x[1])):
    severity = "HIGH" if len(lista) >= 3 else "MEDIUM"
    print(f"### [{severity}] Focus = \"{fk}\" ({len(lista)} productos)")
    for p in lista:
        print(f"    {p['id']:5} | {p['name'][:60]}")
        print(f"          {p['url']}")
    focus_canibal.append({"focus": fk, "severity": severity, "productos": lista})
    print()

print(f"\n## Clusters por SIMILITUD de título (jaccard >= 0.6)\n")
clusters_sorted = sorted(clusters_canibal.values(), key=lambda l: -len(l))
clusters_reportados = []
for cluster in clusters_sorted[:25]:  # top 25
    if len(cluster) < 2:
        continue
    # Verificar si dentro del cluster hay focus keyword unico o duplicado
    focus_set = set(p["focus"].lower() for p in cluster if p["focus"])
    if len(focus_set) == 1 and len(cluster) >= 2 and list(focus_set)[0]:
        sev = "HIGH"
        razon = "mismo focus keyword Y títulos similares"
    elif len(focus_set) > 1:
        sev = "MEDIUM"
        razon = f"títulos similares pero focus keywords distintos ({len(focus_set)} focos)"
    else:
        sev = "LOW"
        razon = "títulos similares sin focus keyword definido"

    print(f"### [{sev}] Cluster de {len(cluster)} productos similares — {razon}")
    for p in cluster:
        print(f"    {p['id']:5} | focus=\"{p['focus'][:25]:25}\" | {p['name'][:55]}")
    print()
    clusters_reportados.append({"severity": sev, "razon": razon, "productos": cluster})

# Guardar JSON
with open(r"C:\Users\dell\victtorino\canibalizacion_resultado.json", "w", encoding="utf-8") as f:
    json.dump({
        "total_productos": len(productos),
        "focus_keyword_duplicados": [
            {"focus": fk, "count": len(v), "productos": [{"id": p["id"], "name": p["name"]} for p in v]}
            for fk, v in focus_dup.items()
        ],
        "clusters_similitud": [
            {"severity": c["severity"], "razon": c["razon"],
             "productos": [{"id": p["id"], "name": p["name"], "focus": p["focus"], "url": p["url"]} for p in c["productos"]]}
            for c in clusters_reportados
        ],
    }, f, ensure_ascii=False, indent=2)
print(f"\nDetalle guardado en canibalizacion_resultado.json")

# Stats
total_focus_dup = sum(len(v) for v in focus_dup.values())
total_clusters = sum(len(c["productos"]) for c in clusters_reportados)
print(f"\nResumen rápido:")
print(f"  Focus keywords duplicados: {len(focus_dup)} grupos, {total_focus_dup} productos involucrados")
print(f"  Clusters por similitud:    {len(clusters_reportados)} grupos, {total_clusters} productos involucrados")
