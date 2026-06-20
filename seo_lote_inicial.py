"""
Aplica SEO inspiracional-hogar a los 2 productos draft recién importados desde ML.
Mantiene status=draft. Actualiza: slug, name, descripcion (HTML), short_description,
Rank Math meta (title/desc/focus_keyword), y alt text por imagen.
"""
import json
import sys
import io
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
KEY = "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15"
SEC = "cs_3604e7ebdb8ff78442731344cc95af50516188a5"


def rank_math_meta(title, desc, focus):
    return [
        {"key": "rank_math_title", "value": title},
        {"key": "rank_math_description", "value": desc},
        {"key": "rank_math_focus_keyword", "value": focus},
    ]


# ---------- PRODUCTO 2537: Columna de Ducha Simple sin Grifería ----------
desc_2537 = """
<h2>Una ducha que se siente como un pequeño respiro al día</h2>
<p>La <strong>columna de ducha simple Victtorino</strong> está pensada para esos
hogares donde el baño deja de ser un espacio funcional y se convierte en el lugar
favorito para empezar y terminar la jornada. Líneas limpias, instalación sin
complicaciones y la promesa de una ducha amplia, envolvente y reconfortante.</p>

<h3>Diseñada para integrarse, no para imponerse</h3>
<p>Su silueta minimalista combina con cualquier estilo de baño: moderno, nórdico,
industrial o clásico renovado. Si estás reformando o simplemente quieres darle
una segunda vida a tu baño, esta columna es el acento perfecto.</p>

<h3>¿Qué incluye?</h3>
<ul>
  <li>Columna de ducha con barra deslizable y altura regulable.</li>
  <li>Soporte ajustable para acomodar a toda la familia.</li>
  <li>Acabado resistente a salpicaduras y manchas de agua dura.</li>
  <li><em>No incluye grifería</em>: la columna se conecta a tu mezcladora o
      monomando existente, lo que te permite renovar solo lo que necesitas.</li>
</ul>

<h3>Pensada para tu casa real</h3>
<p>Instalación accesible para maestros gasfíter y compatible con la mayoría de
las griferías del mercado chileno. Despacho a todo Chile y respaldo Victtorino.</p>

<p><strong>Imagina tu próxima ducha en casa.</strong> Esta columna ya está esperándola.</p>
"""

producto_2537 = {
    "status": "draft",
    "name": "Columna de Ducha Simple sin Grifería",
    "slug": "columna-de-ducha-simple-sin-griferia",
    "short_description": (
        "<p>Empieza el día como mereces. Una columna de ducha elegante y "
        "minimalista que transforma cualquier baño en tu rincón favorito de la casa.</p>"
    ),
    "description": desc_2537.strip(),
    "meta_data": rank_math_meta(
        title="Columna de Ducha Simple sin Grifería | Victtorino",
        desc=(
            "Convierte tu ducha en un momento de calma. Columna minimalista, "
            "fácil de instalar, se conecta a tu grifería actual. Despacho a todo Chile."
        ),
        focus="columna de ducha",
    ),
    "images": [
        {"id": 2533, "alt": "Columna de ducha simple sin grifería en baño moderno"},
        {"id": 2534, "alt": "Detalle del cabezal de la columna de ducha Victtorino"},
        {"id": 2535, "alt": "Columna de ducha instalada en muro de cerámica"},
        {"id": 2536, "alt": "Vista lateral de la columna de ducha con regulador de altura"},
    ],
}

# ---------- PRODUCTO 2543: Set Accesorios Baño Colomba 6 Piezas Plateado ----------
desc_2543 = """
<h2>Los pequeños detalles son los que más se notan</h2>
<p>El <strong>set de accesorios Colomba</strong> de Victtorino es de esos cambios
que parecen menores y terminan transformando por completo la sensación de tu
baño. Seis piezas plateadas, diseño moderno y la armonía visual que solo logras
cuando todo combina entre sí.</p>

<h3>Renueva tu baño sin remodelarlo</h3>
<p>No necesitas demoler nada ni gastar una fortuna. Reemplazar los accesorios
viejos por este set completo es la manera más rápida y económica de darle a tu
baño un aire fresco, moderno y coherente.</p>

<h3>¿Qué incluye el set Colomba?</h3>
<ul>
  <li>Toallero principal en acabado plateado.</li>
  <li>Portarrollos para papel higiénico.</li>
  <li>Jabonera de pared.</li>
  <li>Ganchos para colgar.</li>
  <li>Soporte para vaso o cepillos de dientes.</li>
  <li>Toallero auxiliar / barra adicional.</li>
</ul>

<h3>Una sola colección, una sola estética</h3>
<p>La gracia de comprar el set completo es que <em>todas las piezas conversan
entre sí</em>: misma terminación, mismo lenguaje de diseño, misma calidad.
Adiós al baño con piezas sueltas que parecen no pertenecer al mismo lugar.</p>

<h3>Para hogares chilenos reales</h3>
<p>Instalación simple, fijaciones incluidas, materiales pensados para resistir
la humedad del día a día. Despacho a todo Chile y respaldo Victtorino.</p>
"""

producto_2543 = {
    "status": "draft",
    "name": "Set de Accesorios para Baño Colomba — 6 Piezas Plateado",
    "slug": "set-accesorios-bano-6-piezas-colomba-plateado",
    "short_description": (
        "<p>Detalles que cambian todo. Seis piezas plateadas con diseño moderno "
        "que le dan a tu baño esa armonía que siempre quisiste, sin necesidad de remodelar.</p>"
    ),
    "description": desc_2543.strip(),
    "meta_data": rank_math_meta(
        title="Set Accesorios Baño 6 Piezas Colomba Plateado | Victtorino",
        desc=(
            "Renueva tu baño con un set completo de 6 piezas plateadas. Diseño "
            "moderno, instalación simple. Despacho a todo Chile. Calidad Victtorino."
        ),
        focus="set accesorios para baño",
    ),
    "images": [
        {"id": 2538, "alt": "Set accesorios baño Colomba 6 piezas plateado completo"},
        {"id": 2539, "alt": "Toallero del set Colomba en pared blanca de baño moderno"},
        {"id": 2540, "alt": "Jabonera plateada del set Colomba para pared"},
        {"id": 2541, "alt": "Portarrollos de papel del set Colomba en baño contemporáneo"},
        {"id": 2542, "alt": "Ganchos plateados del set Colomba colgando toallas"},
    ],
}


def actualizar(pid, body):
    url = f"{WC}/wp-json/wc/v3/products/{pid}"
    params = {"consumer_key": KEY, "consumer_secret": SEC}
    r = requests.put(url, json=body, params=params, timeout=60)
    if r.status_code >= 400:
        print(f"ERROR {pid}: HTTP {r.status_code} - {r.text[:400]}")
        return None
    return r.json()


print("=" * 70)
print("Aplicando SEO inspiracional-hogar (mantengo status=draft)")
print("=" * 70)

for pid, body in [(2537, producto_2537), (2543, producto_2543)]:
    print(f"\nProducto {pid}: {body['name'][:60]}")
    res = actualizar(pid, body)
    if res:
        print(f"  status   : {res.get('status')}")
        print(f"  slug     : {res.get('slug')}")
        print(f"  permalink: {res.get('permalink')}")
        print(f"  edit_url : {WC}/wp-admin/post.php?post={pid}&action=edit")
        rm = {m['key']: m['value'] for m in res.get('meta_data', []) if m['key'].startswith('rank_math_')}
        print(f"  rank_math_title: {rm.get('rank_math_title')}")
        print(f"  rank_math_description: {rm.get('rank_math_description')}")
        print(f"  focus_keyword: {rm.get('rank_math_focus_keyword')}")
        alts = [(im['id'], im.get('alt')) for im in res.get('images', [])]
        print(f"  imagenes con alt: {len(alts)} -> {alts}")

print("\nDONE. Ambos productos siguen en DRAFT para tu revision.")
