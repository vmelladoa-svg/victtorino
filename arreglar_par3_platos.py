"""
Par 3 de canibalización: arreglar 1826 (Sin Brazo) y diferenciar 946 (Schwartz).
- 1826: importar 6 fotos de MLC1309864924 + SEO premium completo
- 946: cambiar focus keyword a 'plato de ducha schwartz negro' (sin tocar descripción ni precio)
"""
import json
import sys
import io
import re
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json") as f:
    tk = json.load(f)
H = {"Authorization": f"Bearer {tk['access_token']}"}

# Traer fotos del MLC1309864924
item = requests.get("https://api.mercadolibre.com/items/MLC1309864924", headers=H, timeout=30).json()
pictures = [p["url"] for p in item.get("pictures", []) if p.get("url")]
print(f"Fotos ML del Sin Brazo: {len(pictures)}")

# ============================
# 1826 — SEO premium + fotos
# ============================
desc_1826 = """<h2>Un plato de ducha sin brazo: la opción modular más versátil</h2>
<p>El <strong>plato de ducha sin brazo</strong> es la elección inteligente cuando quieres montar tu cabezal de ducha con tu propia configuración: brazos de muro distintos, conexiones de techo, o reemplazar solo el plato sin tocar el resto del shower. La versión sin brazo te da total libertad para combinar con la grifería que ya tienes o con un brazo nuevo de la longitud exacta que necesitas.</p>
<p>Acero inoxidable de calidad con terminación pulida plateada que se mantiene como nueva después de meses de uso intensivo en baños chilenos reales: vapor permanente, agua dura, productos de limpieza variados.</p>

<h3>Por qué elegir un plato de ducha sin brazo</h3>
<ul>
  <li>Plato cuadrado de 25 x 25 cm — la medida más versátil para shower individual.</li>
  <li>Lluvia uniforme tipo cascada, sin chorros aislados ni gotas duras.</li>
  <li>Acero inoxidable resistente a manchas de agua dura y huellas.</li>
  <li>Sin brazo incluido: tú eliges el brazo de muro o techo que mejor se adapte.</li>
  <li>Conexión estándar 1/2 pulgada compatible con cualquier brazo del mercado chileno.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo conviene un plato sin brazo</h3>
<p>Si ya tienes el brazo instalado y solo quieres renovar el plato, o si tu ducha es de techo (en cuyo caso el brazo es completamente distinto al del muro), o si quieres elegir un brazo de longitud específica para llegar exactamente sobre la persona — todas son razones para preferir un plato de ducha sin brazo. Es la opción más versátil y la más popular entre instaladores con experiencia.</p>
<p>Si necesitas también renovar la grifería del shower, mira nuestro catálogo de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Instalación accesible</h3>
<p>Cualquier maestro gasfíter con experiencia básica lo monta en 10 minutos. Solo necesitas atornillar el plato al brazo existente con teflón en la rosca. Para el brazo, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería y accesorios de baño. Despacho a todo Chile.</p>
<p><strong>El plato de ducha sin brazo es la decisión inteligente cuando quieres configurar tu shower a tu manera.</strong></p>"""

images_payload = [
    {"src": url, "alt": ("Plato de ducha cuadrado 25 cm acero inoxidable sin brazo" if i == 0
                        else f"Plato ducha cuadrado sin brazo - foto {i+1}")[:120]}
    for i, url in enumerate(pictures)
]

body_1826 = {
    "description": desc_1826,
    "short_description": "<p>El <strong>plato de ducha sin brazo</strong> que te da total libertad para configurar tu shower. Acero inoxidable 25 cm, conexión estándar 1/2. Despacho a todo Chile.</p>",
    "images": images_payload,
    "categories": [{"id": 112}, {"id": 113}],  # Accesorios + Griferia
    "meta_data": [
        {"key": "rank_math_title", "value": "Plato de Ducha Sin Brazo Acero Inoxidable 25 cm | Victtorino"},
        {"key": "rank_math_description", "value": "Plato de ducha sin brazo en acero inoxidable de 25 cm. Total libertad para configurar tu shower. Despacho a todo Chile. Victtorino."},
        {"key": "rank_math_focus_keyword", "value": "plato de ducha sin brazo"},
    ],
}

r = requests.put(f"{WC}/wp-json/wc/v3/products/1826", json=body_1826, params=P, timeout=120)
d = r.json()
print(f"\n1826 actualizado: status={r.status_code}")
print(f"  fotos en Woo ahora: {len(d.get('images',[]))}")
print(f"  palabras desc: {len(re.sub(r'<[^>]+>',' ', d.get('description','')).split())}")
print(f"  focus: {next((m['value'] for m in d.get('meta_data',[]) if m['key']=='rank_math_focus_keyword'), '')}")

# ============================
# 946 — solo cambiar focus
# ============================
body_946 = {
    "meta_data": [
        {"key": "rank_math_title", "value": "Plato de Ducha Schwartz Negro Acero 25 cm | Victtorino"},
        {"key": "rank_math_description", "value": "Plato de ducha Schwartz negro en acero 25 cm. Diseño contemporáneo, terminación oscura premium. Despacho a todo Chile. Victtorino."},
        {"key": "rank_math_focus_keyword", "value": "plato de ducha schwartz negro"},
    ],
}
r = requests.put(f"{WC}/wp-json/wc/v3/products/946", json=body_946, params=P, timeout=60)
d = r.json()
print(f"\n946 actualizado: status={r.status_code}")
print(f"  focus nuevo: {next((m['value'] for m in d.get('meta_data',[]) if m['key']=='rank_math_focus_keyword'), '')}")
