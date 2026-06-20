"""1827 Shower Door 80x80x195: importar 7 fotos propias + SEO premium."""
import json, sys, io, re, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}
with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json") as f:
    tk = json.load(f)
H = {"Authorization": f"Bearer {tk['access_token']}"}

item = requests.get("https://api.mercadolibre.com/items/MLC1311147590", headers=H, timeout=30).json()
pics = [p["url"] for p in item.get("pictures", []) if p.get("url")]
print(f"Fotos ML: {len(pics)}")

desc = """<h2>Un shower door 80x80x195 que redefine la ducha</h2>
<p>El <strong>shower door 80x80x195</strong> con receptáculo cuadrado es la solución más completa cuando quieres delimitar la ducha de forma elegante y duradera. La medida 80x80 es la más versátil del mercado chileno — amplia para moverse cómodo pero compacta para baños de departamento y casa. Y los 195 cm de altura son el estándar que cubre cualquier estatura sin recortes en el techo.</p>
<p>Vidrio templado de seguridad, perfilería resistente a humedad permanente y receptáculo antideslizante incluido. Una sola pieza que resuelve la ducha completa: cerramiento, base y seguridad.</p>

<h3>Por qué este shower door 80x80x195 es distinto</h3>
<ul>
  <li>Vidrio templado de seguridad: resiste golpes accidentales sin estallar peligrosamente.</li>
  <li>Perfilería resistente a la humedad permanente del baño chileno.</li>
  <li>Receptáculo cuadrado antideslizante incluido — no hay que comprarlo aparte.</li>
  <li>Diseño cuadrado contemporáneo que aprovecha la esquina del baño.</li>
  <li>Altura 195 cm: cubre cualquier estatura y techo estándar chileno.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo conviene un shower door 80x80x195</h3>
<p>Si tu ducha actual es de cortina o no tiene cerramiento, instalar un shower door 80x80x195 es probablemente la intervención de mayor impacto visual con menor obra. El resto del baño se mantiene seco mientras alguien se ducha, el vapor se contiene, las toallas no quedan húmedas. Pequeños cambios diarios que se acumulan en años.</p>
<p>Si vas a renovar más del shower, mira nuestra <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Instalación con maestro especializado</h3>
<p>Recomendamos instalación con maestro con experiencia en mamparas. La pieza viene completa con perfilería, vidrios, receptáculo y herrajes. Para seguridad adicional dentro de la ducha, mira nuestras <a href="https://victtorino.cl/categoria-producto/agarraderas-y-barras-para-bano/">agarraderas y barras de seguridad</a>.</p>

<h3>Pensado para baños chilenos reales</h3>
<p>El uso real de una ducha en una casa chilena pone a prueba cualquier shower door: vapor diario, agua caliente, productos de limpieza, baños familiares con frecuencia alta. Este shower door 80x80x195 está elegido para resistir ese contexto durante años, no temporadas.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en mamparas y receptáculos. Despacho a todo Chile.</p>
<p><strong>Tu ducha diaria, como debería sentirse.</strong></p>"""

images_payload = [
    {"src": u, "alt": ("Shower door 80x80x195 cuadrado vidrio templado" if i == 0
                       else f"Shower door 80x80x195 - foto {i+1}")[:120]}
    for i, u in enumerate(pics)
]

body = {
    "name": "Shower Door 80x80x195 Cuadrado Transparente Vidrio Templado",
    "description": desc,
    "short_description": "<p>El <strong>shower door 80x80x195</strong> con receptáculo cuadrado: vidrio templado de seguridad, perfilería resistente y diseño contemporáneo que delimita la ducha sin obras grandes. Despacho a todo Chile.</p>",
    "images": images_payload,
    "meta_data": [
        {"key": "rank_math_title", "value": "Shower Door 80x80x195 Cuadrado Vidrio Templado | Victtorino"},
        {"key": "rank_math_description", "value": "Shower door 80x80x195 cuadrado con receptáculo. Vidrio templado, perfilería resistente. Despacho a todo Chile. Calidad Victtorino."},
        {"key": "rank_math_focus_keyword", "value": "shower door 80x80x195"},
    ],
}

r = requests.put(f"{WC}/wp-json/wc/v3/products/1827", json=body, params=P, timeout=120)
d = r.json()
print(f"status: {r.status_code}")
print(f"  name: {d.get('name')}")
print(f"  fotos: {len(d.get('images',[]))}")
print(f"  palabras desc: {len(re.sub(r'<[^>]+>',' ', d.get('description','')).split())}")
print(f"  focus: {next((m['value'] for m in d.get('meta_data',[]) if m['key']=='rank_math_focus_keyword'), '')}")
