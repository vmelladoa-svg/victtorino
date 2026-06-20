"""
Importa 5 productos Chilat a WooCommerce como BORRADOR (status=draft, sin publicar).
- SKU prefijado CL-TEST-<goodsId>  -> identificables y borrables en bloque.
- Solo fotos cuadradas (descarta infografías con texto chino, ratio fuera de 0.7-1.5).
- WC descarga las fotos (de alicdn) y las re-hospeda en victtorino.cl (sin dependencia externa).
- Sin precio (queda en draft para que se revise/reescriba el titulo).
Borrar luego: ver chilat_borrar_draft.py
"""
import json, sys, io, re, requests
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
ROOT = Path(r"C:\Users\dell\victtorino")

WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"

JUNK = [
    r"transfronteriz[oa]s?", r"canci[oó]n de la vida", r"life'?s? song", r"life song",
    r"uno por uno", r"al por mayor", r"comercio exterior", r"cruz[-\s]?frontera",
    r"celebridad de internet", r"amazon", r"guangrun", r"qianxi\s*(bird|niao)?",
    r"shengruijia", r"ventas? directas? de f[aá]brica", r"f[aá]brica al por mayor",
    r"pistola", r"\[[^\]]*\]", r"\b(rv|de los ni[nñ]os)\b",
]

def limpiar_titulo(t):
    t = t or ""
    for p in JUNK:
        t = re.sub(p, " ", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ,.-")
    t = t[:1].upper() + t[1:] if t else "Producto"
    return t.strip()

def wc_post(path, body):
    r = requests.post(f"{WC}/wp-json/wc/v3{path}",
                      params={"consumer_key": KEY, "consumer_secret": SEC},
                      json=body, timeout=180)
    return r

manifest = json.load(open(ROOT / "chilat_pick5_manifest.json", encoding="utf-8"))
creados = []
for prod in manifest:
    gid = prod["goodsId"]
    sku = f"CL-TEST-{gid}"
    titulo = limpiar_titulo(prod["nombre"])
    # solo fotos cuadradas (limpias)
    fotos = [f for f in prod["fotos"] if 0.7 <= f["ratio"] <= 1.5]
    imgs = [{"src": f["url"], "position": i} for i, f in enumerate(fotos)]

    # evitar duplicado
    ex = requests.get(f"{WC}/wp-json/wc/v3/products",
                      params={"consumer_key": KEY, "consumer_secret": SEC, "sku": sku},
                      timeout=30).json()
    if ex:
        print(f"[{gid}] ya existe (id={ex[0]['id']}) -> salto")
        creados.append({"goodsId": gid, "woo_id": ex[0]["id"], "estado": "ya_existia"})
        continue

    body = {
        "name": titulo,
        "type": "simple",
        "status": "draft",
        "catalog_visibility": "hidden",
        "sku": sku,
        "description": "",
        "short_description": "BORRADOR DE PRUEBA - reescribir titulo y descripcion antes de publicar.",
        "images": imgs,
    }
    print(f"[{gid}] creando draft '{titulo[:40]}' con {len(imgs)}/{len(prod['fotos'])} fotos limpias...")
    r = wc_post("/products", body)
    if r.status_code >= 400:
        print(f"   ERROR {r.status_code}: {r.text[:200]}")
        creados.append({"goodsId": gid, "estado": f"error_{r.status_code}"})
        continue
    j = r.json()
    print(f"   OK woo_id={j['id']} status={j['status']} fotos_en_web={len(j.get('images',[]))}")
    creados.append({"goodsId": gid, "woo_id": j["id"], "titulo": titulo,
                    "precio_usd_origen": prod["precio_usd"], "fotos": len(j.get("images", [])),
                    "edit_url": f"{WC}/wp-admin/post.php?post={j['id']}&action=edit",
                    "estado": "creado"})

json.dump(creados, open(ROOT / "chilat_draft_resultado.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\n=== RESUMEN ===")
for c in creados:
    if c.get("estado") == "creado":
        print(f"  woo#{c['woo_id']}  ${c['precio_usd_origen']:>7} USD costo  {c['fotos']}f  {c['titulo'][:45]}")
        print(f"     editar: {c['edit_url']}")
