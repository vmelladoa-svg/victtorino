"""
Importa 23 productos faltantes de ML C3 a WooCommerce como DRAFT.

Flujo:
1. Crea 3 categorias nuevas en Woo (Agarraderas y Barras, Sifones y Desagues, WC e Inodoros).
2. Trae detalle ML de cada item.
3. Construye SEO inspiracional-hogar (slug, meta, descripcion HTML, alt text) usando plantillas por categoria destino.
4. POST a Woo con status=draft + categoria asignada.
5. Reporta IDs + URLs.

Todo queda en DRAFT para revision.
"""
import json
import sys
import io
import re
import time
import unicodedata
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"
PARAMS = {"consumer_key": KEY, "consumer_secret": SEC}

with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json", encoding="utf-8") as f:
    tk = json.load(f)
ML_HEAD = {"Authorization": f"Bearer {tk['access_token']}"}

# Listado fijo del cruce
FALTANTES = json.load(open(r"C:\Users\dell\victtorino\cruce_ml_woo_resultado.json", encoding="utf-8"))["faltantes"]


def slugify(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]


def woo_get(path, params=None):
    p = {**PARAMS, **(params or {})}
    r = requests.get(f"{WC}/wp-json/wc/v3{path}", params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def woo_post(path, body, intentos=3):
    for n in range(1, intentos + 1):
        try:
            r = requests.post(f"{WC}/wp-json/wc/v3{path}", json=body, params=PARAMS, timeout=120)
            if r.status_code >= 400:
                print(f"  WOO ERROR {r.status_code} en POST {path}: {r.text[:300]}")
                return None
            return r.json()
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            espera = 2 ** n
            print(f"  RED intento {n}/{intentos} fallo ({type(e).__name__}); reintento en {espera}s")
            time.sleep(espera)
    print(f"  ABORTO tras {intentos} intentos")
    return None


def existe_sku_en_woo(sku):
    """Verifica si ya hay un producto con este SKU."""
    try:
        r = requests.get(f"{WC}/wp-json/wc/v3/products", params={**PARAMS, "sku": sku}, timeout=30)
        d = r.json()
        if d:
            return d[0]
    except Exception:
        pass
    return None


def woo_put(path, body):
    r = requests.put(f"{WC}/wp-json/wc/v3{path}", json=body, params=PARAMS, timeout=60)
    if r.status_code >= 400:
        print(f"WOO ERROR {r.status_code} en PUT {path}: {r.text[:400]}")
        return None
    return r.json()


def ml_get(path):
    r = requests.get(f"https://api.mercadolibre.com{path}", headers=ML_HEAD, timeout=30)
    r.raise_for_status()
    return r.json()


# ============================================================
# PASO 1: Crear 3 categorias nuevas
# ============================================================
NUEVAS_CATEGORIAS = [
    {
        "name": "Agarraderas y Barras",
        "slug": "agarraderas-y-barras-para-bano",
        "description": (
            "<p>Las agarraderas y barras de seguridad son ese gesto silencioso que "
            "convierte un baño común en un espacio seguro y pensado para toda la "
            "familia. Ya sea para abuelos, niños, personas con movilidad reducida o "
            "simplemente para añadir un punto extra de tranquilidad a la ducha del "
            "día a día, instalarlas es una de las decisiones más valoradas cuando se "
            "vive el baño. En Victtorino seleccionamos modelos en acero inoxidable y "
            "acabados resistentes a la humedad, con anclajes seguros y diseño que se "
            "integra al baño moderno sin gritar \"barra de hospital\". Tranquilidad "
            "en cada paso.</p>"
        ),
    },
    {
        "name": "Sifones y Desagües",
        "slug": "sifones-y-desagues",
        "description": (
            "<p>El sifón es uno de esos elementos que nadie celebra cuando funciona, "
            "pero que se vuelve protagonista cuando falla. Un buen sifón evita malos "
            "olores, atascos y filtraciones — silencioso, eficiente, invisible. En "
            "Victtorino reunimos sifones para lavamanos, lavaplatos, tinas y "
            "receptáculos, en materiales que aguantan el uso real de un hogar "
            "chileno: cromados resistentes, bronce duradero y diseños pensados para "
            "que la instalación sea rápida y limpia. Renueva lo que no se ve y nota "
            "la diferencia.</p>"
        ),
    },
    {
        "name": "WC e Inodoros",
        "slug": "wc-e-inodoros",
        "description": (
            "<p>El WC es la pieza más usada del baño y, sin embargo, la que menos "
            "atención recibe a la hora de renovar. Tapas que no cierran bien, "
            "válvulas que gotean, fluxómetros que se quedan trabados: pequeños "
            "detalles que terminan condicionando toda la experiencia. Victtorino "
            "ofrece tapas de WC, válvulas de descarga, fluxómetros, válvulas de pie "
            "y accesorios pensados tanto para el hogar como para baños "
            "institucionales. Calidad que se nota al cerrar la puerta.</p>"
        ),
    },
]

print("=" * 70)
print("PASO 1: Creando 3 categorias nuevas")
print("=" * 70)

# Cache de categorias existentes
cats_existentes = {}
for c in woo_get("/products/categories", {"per_page": 100}):
    cats_existentes[c["name"].lower().strip()] = c["id"]

cat_nuevas_creadas = {}
for cat in NUEVAS_CATEGORIAS:
    nombre_low = cat["name"].lower().strip()
    if nombre_low in cats_existentes:
        cat_nuevas_creadas[cat["name"]] = cats_existentes[nombre_low]
        print(f"  YA EXISTIA: '{cat['name']}' (id={cats_existentes[nombre_low]})")
        continue
    res = woo_post("/products/categories", cat)
    if res:
        cat_nuevas_creadas[cat["name"]] = res["id"]
        print(f"  CREADA: '{cat['name']}' (id={res['id']}, slug={res['slug']})")
        cats_existentes[nombre_low] = res["id"]
    else:
        print(f"  FALLO al crear '{cat['name']}'")
        sys.exit(1)

# Cargar mapeo a IDs Woo (existentes + nuevas)
def cat_id(nombre):
    return cats_existentes.get(nombre.lower().strip())


# ============================================================
# PASO 2: Mapeo categoria ML -> categoria Woo + plantilla SEO
# ============================================================

# (cat_woo, focus_keyword_base, intro_html, secciones_html_factory)
def plantilla_griferia(titulo):
    return (
        "<h2>Una grifería que se siente al primer uso</h2>"
        f"<p>La <strong>{titulo}</strong> de Victtorino combina diseño contemporáneo "
        "y materiales pensados para resistir el día a día del agua dura chilena. "
        "Una pieza que no solo cumple su función, sino que aporta carácter al baño.</p>"
        "<h3>Diseño y materiales</h3>"
        "<ul><li>Acabado resistente a manchas y huellas</li>"
        "<li>Mecanismo cerámico de larga duración</li>"
        "<li>Compatible con instalaciones estándar del mercado chileno</li>"
        "<li>Despacho a todo Chile con respaldo Victtorino</li></ul>"
        "<h3>Renueva sin remodelar</h3>"
        "<p>Cambiar la grifería es una de las intervenciones de mayor impacto visual "
        "con menor inversión. Una llave nueva refresca todo el baño.</p>"
    )

def plantilla_accesorios(titulo):
    return (
        "<h2>Los detalles que cambian la sensación del baño</h2>"
        f"<p>El <strong>{titulo}</strong> es de esos accesorios que parecen menores "
        "pero terminan ordenando visualmente todo el espacio. Diseño funcional, "
        "materiales resistentes y la armonía estética que tu baño se merece.</p>"
        "<h3>Pensado para tu rutina diaria</h3>"
        "<ul><li>Materiales pensados para resistir humedad</li>"
        "<li>Instalación accesible</li>"
        "<li>Acabados que combinan con cualquier estilo de baño</li>"
        "<li>Despacho a todo Chile</li></ul>"
        "<p>Renovar accesorios es la forma más simple y económica de darle un aire "
        "fresco a tu baño sin necesidad de remodelaciones.</p>"
    )

def plantilla_dispensador(titulo):
    return (
        "<h2>Higiene moderna, gesto silencioso</h2>"
        f"<p>Un <strong>{titulo}</strong> bien elegido es uno de esos detalles que "
        "elevan la experiencia del baño sin que se note. Dosis controlada, sin "
        "goteos, sin restos pegajosos en el lavamanos.</p>"
        "<h3>Pensado para uso real</h3>"
        "<ul><li>Diseño ergonómico, fácil de rellenar</li>"
        "<li>Materiales resistentes a productos químicos suaves</li>"
        "<li>Ideal para hogares, oficinas y locales comerciales</li>"
        "<li>Despacho a todo Chile</li></ul>"
    )

def plantilla_espejos(titulo):
    return (
        "<h2>Un espejo es más que un reflejo</h2>"
        f"<p>El <strong>{titulo}</strong> es de esas piezas que amplían visualmente "
        "el baño y mejoran la iluminación natural. La diferencia entre un baño "
        "funcional y un baño que se siente cuidado.</p>"
        "<h3>Diseño y funcionalidad</h3>"
        "<ul><li>Bordes y soportes diseñados para resistir humedad</li>"
        "<li>Acabados pensados para integrarse a cualquier estilo</li>"
        "<li>Anclajes seguros incluidos</li>"
        "<li>Despacho a todo Chile</li></ul>"
    )

def plantilla_shower(titulo):
    return (
        "<h2>El espacio de la ducha como protagonista</h2>"
        f"<p>El <strong>{titulo}</strong> redefine el área húmeda del baño. Una "
        "ducha bien delimitada se siente más amplia, más limpia y más privada.</p>"
        "<h3>Diseño y seguridad</h3>"
        "<ul><li>Materiales pensados para resistir humedad permanente</li>"
        "<li>Compatible con instalaciones estándar</li>"
        "<li>Despacho a todo Chile</li></ul>"
    )

def plantilla_lavaplatos(titulo):
    return (
        "<h2>El corazón funcional de la cocina</h2>"
        f"<p>El <strong>{titulo}</strong> está pensado para soportar el ritmo real "
        "de una cocina chilena: lavados largos, agua caliente, ollas grandes y uso "
        "intensivo. Materiales resistentes y diseño que aguanta.</p>"
        "<h3>Pensado para tu cocina</h3>"
        "<ul><li>Acero inoxidable resistente a manchas</li>"
        "<li>Dimensiones estándar para muebles de cocina chilenos</li>"
        "<li>Despacho a todo Chile con respaldo Victtorino</li></ul>"
    )

def plantilla_lavamanos(titulo):
    return (
        "<h2>El lavamanos como pieza decorativa</h2>"
        f"<p>El <strong>{titulo}</strong> deja atrás la idea del lavamanos puramente "
        "funcional. Diseño contemporáneo que transforma el baño en un espacio "
        "cuidado y memorable.</p>"
        "<h3>Diseño y calidad</h3>"
        "<ul><li>Materiales pensados para el uso diario</li>"
        "<li>Instalación compatible con mesones y muebles estándar</li>"
        "<li>Despacho a todo Chile</li></ul>"
    )

def plantilla_agarraderas(titulo):
    return (
        "<h2>Seguridad sin perder el estilo</h2>"
        f"<p>La <strong>{titulo}</strong> es ese gesto silencioso que transforma "
        "el baño en un espacio más seguro para toda la familia. Diseño moderno que "
        "no grita \"barra de hospital\" — se integra al baño sin sacrificar la "
        "estética.</p>"
        "<h3>Pensada para la vida real</h3>"
        "<ul><li>Acero inoxidable resistente a la corrosión</li>"
        "<li>Anclajes seguros para muros sólidos</li>"
        "<li>Acabado que combina con cualquier baño moderno</li>"
        "<li>Tranquilidad en cada paso, especialmente con adultos mayores o niños</li></ul>"
    )

def plantilla_sifones(titulo):
    return (
        "<h2>Lo que no se ve también importa</h2>"
        f"<p>El <strong>{titulo}</strong> es uno de esos elementos que nadie celebra "
        "cuando funcionan, pero que evitan dolores de cabeza diarios: malos olores, "
        "filtraciones, atascos. Silencioso, eficiente, invisible.</p>"
        "<h3>Calidad que se nota a largo plazo</h3>"
        "<ul><li>Materiales resistentes al desgaste por agua</li>"
        "<li>Instalación accesible para maestros gasfíter</li>"
        "<li>Compatible con instalaciones estándar chilenas</li>"
        "<li>Despacho a todo Chile con respaldo Victtorino</li></ul>"
    )

def plantilla_wc(titulo):
    return (
        "<h2>Detalles que mejoran la pieza más usada del baño</h2>"
        f"<p>El <strong>{titulo}</strong> es de esos elementos que parecen menores "
        "pero condicionan toda la experiencia del baño. Una válvula que cierra "
        "bien, una tapa que no se afloja, un mecanismo que dura — diferencias "
        "diarias.</p>"
        "<h3>Pensado para uso intensivo</h3>"
        "<ul><li>Materiales resistentes al uso diario</li>"
        "<li>Compatible con instalaciones estándar</li>"
        "<li>Ideal para hogar, oficina y baños institucionales</li>"
        "<li>Despacho a todo Chile</li></ul>"
    )


# Mapeo: ML cat hoja -> (cat_woo_destino, plantilla, focus_kw_template)
MAPEO = {
    "Dispensadores de Jabón":        ("Dispensador", plantilla_dispensador, "dispensador de jabón"),
    "De Jabón y Alcohol en Gel":     ("Dispensador", plantilla_dispensador, "dispensador de jabón"),
    "De Papel":                       ("Accesorios", plantilla_accesorios, "dispensador papel higiénico"),
    "Mamparas y Cabinas":            ("Shower/Mamparas/Receptaculos", plantilla_shower, "mampara shower door"),
    "Griferías Convencionales":      ("Griferia", plantilla_griferia, "llave grifería"),
    "Sets de Duchador y Grifería":   ("Griferia", plantilla_griferia, "set de ducha"),
    "Repisas Esquineras":            ("Accesorios", plantilla_accesorios, "organizador ducha"),
    "Espejos":                        ("Espejos", plantilla_espejos, "espejo baño"),
    "Espejitos":                      ("Espejos", plantilla_espejos, "espejo baño aumento"),
    "Agarraderas":                   ("Agarraderas y Barras", plantilla_agarraderas, "agarradera baño"),
    "Basureros":                      ("Accesorios", plantilla_accesorios, "basurero baño pedal"),
    "Cestos de Residuos":            ("Accesorios", plantilla_accesorios, "basurero pedal"),
    "Jaboneras":                      ("Accesorios", plantilla_accesorios, "jabonera baño"),
    "Sifones de Desague":            ("Sifones y Desagües", plantilla_sifones, "sifón desagüe"),
    "Lavaplatos de Cocina":          ("Lavaplatos", plantilla_lavaplatos, "lavaplatos cocina"),
    "Lavamanos":                      ("Lavamanos", plantilla_lavamanos, "lavamanos baño"),
    "Otros":                          ("WC e Inodoros", plantilla_wc, "válvula WC"),  # solo es la valvula de pie
}


def construir_meta_title(name):
    t = f"{name} | Victtorino"
    if len(t) > 60:
        # acorta el nombre antes del separador
        max_name = 60 - len(" | Victtorino")
        t = f"{name[:max_name].rstrip()} | Victtorino"
    return t


def construir_meta_desc(name, cat_destino, stock):
    plantillas = {
        "Griferia": f"{name}. Diseño moderno y materiales resistentes para tu baño. Despacho a todo Chile. Calidad Victtorino.",
        "Accesorios": f"{name}. Pequeños detalles que renuevan tu baño sin remodelar. Despacho a todo Chile. Calidad Victtorino.",
        "Dispensador": f"{name}. Higiene moderna con diseño elegante para baño y oficina. Despacho a todo Chile. Victtorino.",
        "Espejos": f"{name}. Amplía visualmente tu baño con un espejo bien elegido. Despacho a todo Chile. Calidad Victtorino.",
        "Shower/Mamparas/Receptaculos": f"{name}. Renueva tu ducha con materiales resistentes y diseño contemporáneo. Despacho a todo Chile.",
        "Lavaplatos": f"{name}. Acero inoxidable para soportar el ritmo real de tu cocina. Despacho a todo Chile. Victtorino.",
        "Lavamanos": f"{name}. Diseño contemporáneo que transforma tu baño. Despacho a todo Chile. Calidad Victtorino.",
        "Agarraderas y Barras": f"{name}. Seguridad sin perder el estilo. Acero inoxidable, anclajes seguros. Despacho a todo Chile.",
        "Sifones y Desagües": f"{name}. Sin filtraciones, sin malos olores. Materiales resistentes. Despacho a todo Chile.",
        "WC e Inodoros": f"{name}. Pensado para uso intensivo en hogar y oficina. Despacho a todo Chile. Calidad Victtorino.",
    }
    desc = plantillas.get(cat_destino, f"{name}. Calidad Victtorino con despacho a todo Chile.")
    return desc[:155]


def detalle_ml(item_id):
    item = requests.get(f"https://api.mercadolibre.com/items/{item_id}",
                        headers=ML_HEAD, timeout=30).json()
    try:
        desc = requests.get(f"https://api.mercadolibre.com/items/{item_id}/description",
                            headers=ML_HEAD, timeout=30).json()
        plain = desc.get("plain_text", "") or ""
    except Exception:
        plain = ""
    return item, plain


# ============================================================
# PASO 3 y 4: Procesar los 23 faltantes
# ============================================================
print()
print("=" * 70)
print(f"PASO 2: Importando {len(FALTANTES)} productos faltantes como DRAFT")
print("=" * 70)

resultados = []
errores = []

for idx, f in enumerate(FALTANTES, start=1):
    mid = f["ml_id"]
    ml_cat = f["ml_cat"]
    sku = f"ML-{mid}"

    ya = existe_sku_en_woo(sku)
    if ya:
        print(f"({idx:2}/{len(FALTANTES)}) {mid} -> YA EXISTE (Woo {ya['id']}, status={ya['status']}). Skip.")
        resultados.append({
            "ml_id": mid, "ml_titulo": ya["name"], "ml_cat": ml_cat,
            "woo_id": ya["id"], "woo_cat": "(ya existia)",
            "permalink": ya.get("permalink"),
            "edit_url": f"{WC}/wp-admin/post.php?post={ya['id']}&action=edit",
            "stock": ya.get("stock_quantity"), "precio": ya.get("regular_price"),
            "reused": True,
        })
        continue

    mapeo = MAPEO.get(ml_cat)
    if not mapeo:
        errores.append({"ml_id": mid, "razon": f"sin mapeo para cat '{ml_cat}'"})
        print(f"\n({idx}/{len(FALTANTES)}) ML {mid}: SIN MAPEO ({ml_cat})")
        continue

    cat_woo_nombre, plantilla, focus_base = mapeo
    woo_cat_id = cat_id(cat_woo_nombre)
    if not woo_cat_id:
        errores.append({"ml_id": mid, "razon": f"no encuentro id de Woo para '{cat_woo_nombre}'"})
        print(f"\n({idx}/{len(FALTANTES)}) ML {mid}: NO HAY ID PARA '{cat_woo_nombre}'")
        continue

    item, desc_ml = detalle_ml(mid)
    titulo_original = item.get("title", "Sin titulo")
    # name limpio: title-case suave
    name_woo = titulo_original

    precio = item.get("price")
    stock = int(item.get("available_quantity") or 0)
    pictures = [p["url"] for p in item.get("pictures", []) if p.get("url")]

    slug = slugify(name_woo)
    meta_t = construir_meta_title(name_woo)
    meta_d = construir_meta_desc(name_woo, cat_woo_nombre, stock)
    desc_html = plantilla(name_woo)
    short_desc = (
        f"<p>{name_woo}. Calidad Victtorino con despacho a todo Chile. "
        "Detalles que transforman tu baño sin remodelar.</p>"
    )
    # Alt text: descriptivo por imagen
    images_payload = []
    for i, url in enumerate(pictures, start=1):
        alt = f"{name_woo}" if i == 1 else f"{name_woo} - foto {i}"
        images_payload.append({"src": url, "alt": alt[:120]})

    body = {
        "name": name_woo,
        "slug": slug,
        "type": "simple",
        "status": "draft",
        "regular_price": str(int(precio)) if precio is not None else "",
        "manage_stock": True,
        "stock_quantity": stock,
        "description": desc_html,
        "short_description": short_desc,
        "sku": f"ML-{mid}",
        "categories": [{"id": woo_cat_id}],
        "images": images_payload,
        "meta_data": [
            {"key": "rank_math_title", "value": meta_t},
            {"key": "rank_math_description", "value": meta_d},
            {"key": "rank_math_focus_keyword", "value": focus_base},
        ],
    }

    nuevo = woo_post("/products", body)
    if not nuevo:
        errores.append({"ml_id": mid, "razon": "POST woo fallo"})
        continue
    resultados.append({
        "ml_id": mid,
        "ml_titulo": titulo_original,
        "ml_cat": ml_cat,
        "woo_id": nuevo["id"],
        "woo_cat": cat_woo_nombre,
        "permalink": nuevo.get("permalink"),
        "edit_url": f"{WC}/wp-admin/post.php?post={nuevo['id']}&action=edit",
        "stock": stock,
        "precio": precio,
    })
    print(f"({idx:2}/{len(FALTANTES)}) {mid} -> Woo {nuevo['id']} [{cat_woo_nombre}] {titulo_original[:50]}")

# ============================================================
# REPORTE FINAL
# ============================================================
print()
print("=" * 70)
print(f"RESUMEN: {len(resultados)} creados, {len(errores)} errores")
print("=" * 70)
print()
print(f"{'Woo ID':<8} {'Categoria':<32} {'Titulo':<60}")
print("-" * 100)
for r in resultados:
    print(f"{r['woo_id']:<8} {r['woo_cat'][:32]:<32} {r['ml_titulo'][:60]:<60}")

with open(r"C:\Users\dell\victtorino\lote23_resultado.json", "w", encoding="utf-8") as f:
    json.dump({"creados": resultados, "errores": errores, "categorias_nuevas": cat_nuevas_creadas},
              f, ensure_ascii=False, indent=2)
print("\nDetalle -> lote23_resultado.json")
print("\nTodos los productos quedaron en DRAFT.")
