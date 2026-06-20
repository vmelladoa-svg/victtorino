"""
SEO Premium INDIVIDUAL (manual, no plantilla) para los 10 productos mas
vendidos en ML C3. Cada uno con descripcion unica, focus Google Chile,
~500 palabras, enlaces internos + externo, alt text.

Tambien importa 2 productos que no estaban en la web (lavaplatos 80x44 izq
y llave doble lavadora).
"""
import json
import sys
import io
import time
import re
import unicodedata
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

with open(r"C:\Users\dell\victtorino\tokens_cuenta3.json", encoding="utf-8") as f:
    tk = json.load(f)
ML_HEAD = {"Authorization": f"Bearer {tk['access_token']}"}


def slugify(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]


# ============================================================
# DESCRIPCIONES PREMIUM POR PRODUCTO
# Cada producto: action POST (import) o PUT (update). Datos: name (opcional para update),
# focus, meta_title, meta_desc, short_desc, description, slug (opcional)
# ============================================================

PROD_1814 = {  # #1 — Sifón Desagüe 90mm Receptáculo (179 ventas)
    "action": "PUT", "woo_id": 1814,
    "focus": "sifón desagüe ducha",
    "meta_title": "Sifón Desagüe Ducha 90mm para Receptáculo | Victtorino",
    "meta_desc": "Sifón desagüe ducha de 90mm para receptáculos. Material durable, sin malos olores, instalación accesible. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>sifón desagüe ducha</strong> que evita malos olores y filtraciones. 90mm compatible con la mayoría de receptáculos chilenos. Despacho a todo Chile.</p>",
    "description": """<h2>Un sifón desagüe ducha que se nota cuando funciona mal</h2>
<p>El <strong>sifón desagüe ducha</strong> es una de esas piezas invisibles del baño que solo se vuelven protagonistas cuando algo falla: malos olores subiendo desde el desagüe, agua que se acumula en el plato, filtraciones bajo el receptáculo. Cuando un sifón desagüe ducha funciona bien, simplemente no piensas en él. Cuando funciona mal, condiciona toda la experiencia de la ducha diaria.</p>
<p>Esta pieza de 90 milímetros está pensada para los receptáculos más comunes del mercado chileno. Material durable, sello hermético que aísla el baño del sistema de alcantarillado, y una instalación accesible que cualquier maestro gasfíter resuelve en una visita.</p>

<h3>Por qué este sifón desagüe ducha es distinto</h3>
<ul>
  <li>Sello hermético que bloquea malos olores del alcantarillado de forma permanente.</li>
  <li>Diámetro de 90 mm compatible con la mayoría de receptáculos chilenos estándar.</li>
  <li>Material resistente a la cloración del agua potable y a productos de limpieza.</li>
  <li>Diseño que facilita la limpieza interna sin tener que desarmar todo el receptáculo.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo cambiar el sifón desagüe ducha</h3>
<p>Si sientes olor a alcantarillado en el baño, si el agua se acumula y tarda en bajar después de la ducha, o si notas humedad en el cielo del piso de abajo, probablemente el sifón cumplió su ciclo. No es una falla mayor — es una pieza desechable diseñada para reemplazarse cada cierto tiempo, especialmente en hogares con uso intensivo.</p>
<p>Si vas a renovar más componentes del shower, mira nuestro catálogo de <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>

<h3>Instalación accesible para tu gasfíter</h3>
<p>Cualquier maestro con experiencia básica lo cambia en menos de una hora. Cierras el paso de agua, desmontas el receptáculo solo lo necesario, retiras el sifón viejo, y conectas el nuevo con su empaque incluido. Sin sorpresas, sin obras adicionales.</p>
<p>Si necesitas también renovar la grifería de la ducha, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en sifones y accesorios para baño. Despacho a todo Chile con respaldo de garantía.</p>
<p><strong>Renueva lo que no se ve y nota la diferencia en cada ducha.</strong> Un buen sifón desagüe ducha es la inversión de mayor impacto por menor costo en todo el baño.</p>""",
}

PROD_2734 = {  # #2 — Desagüe Lavaplatos 3 1/2 con Rebalse (86 ventas)
    "action": "PUT", "woo_id": 2734,
    "focus": "desagüe lavaplatos",
    "meta_title": "Desagüe Lavaplatos 3 1/2 con Rebalse 114mm | Victtorino",
    "meta_desc": "Desagüe lavaplatos 3 1/2 (114 mm) con rebalse y reja. Acero plateado durable, instalación accesible. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>desagüe lavaplatos</strong> 3 1/2 con rebalse que tu cocina necesita. Acero durable, reja de calidad, sin filtraciones bajo el mueble. Despacho a todo Chile.</p>",
    "description": """<h2>Un desagüe lavaplatos que aguanta el ritmo real de tu cocina</h2>
<p>El <strong>desagüe lavaplatos</strong> es una de esas piezas que se desgasta más rápido de lo que uno cree: agua caliente todos los días, restos de comida, productos de limpieza variados, golpes de ollas y sartenes. Por eso vale la pena elegir uno que esté hecho para durar, no uno barato que toque cambiar en seis meses.</p>
<p>Este modelo de 3 1/2 pulgadas (equivalente a 11,4 cm o 114 mm) incluye rebalse para evitar desbordes y reja de calidad que filtra los sólidos antes del sifón. El acabado plateado se mantiene como nuevo después de meses de uso intensivo en cocinas chilenas reales.</p>

<h3>Por qué este desagüe lavaplatos es distinto</h3>
<ul>
  <li>Diámetro de 3 1/2 pulgadas (114 mm), la medida más común del mercado chileno.</li>
  <li>Sistema de rebalse incorporado: evita desbordamientos si olvidas cerrar la llave.</li>
  <li>Reja diseñada para filtrar restos sin atascarse fácilmente.</li>
  <li>Acabado plateado resistente a manchas de agua dura y productos químicos suaves.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo cambiar el desagüe lavaplatos</h3>
<p>Si el agua tarda en bajar, si notas malos olores subiendo desde el desagüe, si hay filtraciones bajo el mueble de cocina o si el rebalse se ve oxidado, es hora de cambiarlo. Es una de esas reparaciones que valen mucho más el sábado en la mañana que esperar a que el problema se agrave y termine dañando el mueble.</p>
<p>Si vas a renovar el lavaplatos completo, mira nuestro catálogo de <a href="https://victtorino.cl/categoria-producto/lavaplatos/">lavaplatos de cocina</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a> para complementar.</p>

<h3>Instalación accesible</h3>
<p>Cualquier maestro gasfíter con experiencia básica lo cambia en 30-45 minutos. Cierras la llave de paso, retiras el sifón, sacas el desagüe viejo, conectas el nuevo con su empaque incluido. Sin obras, sin polvo, sin sorpresas.</p>
<p>Para complementar tu cocina, también puedes mirar nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para cocina</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en accesorios de cocina y baño. Despacho a todo Chile con respaldo de garantía.</p>
<p><strong>Una cocina sin filtraciones empieza por un buen desagüe lavaplatos.</strong></p>""",
}

PROD_NEW_LAVAPLATOS_80_IZQ = {  # #3 — Lavaplatos Empotrado 80x44 Izquierdo (77 ventas) — IMPORT
    "action": "POST", "ml_id": "MLC1306255939",
    "cat_destino": "Lavaplatos",
    "focus": "lavaplatos empotrado 80x44",
    "meta_title": "Lavaplatos Empotrado 80x44 Secador Izquierdo | Victtorino",
    "meta_desc": "Lavaplatos empotrado 80x44 cm con secador izquierdo. Acero inoxidable durable para tu cocina chilena. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>lavaplatos empotrado 80x44</strong> con secador izquierdo que tu cocina chilena necesita. Acero inoxidable durable, dimensiones estándar, instalación directa. Despacho a todo Chile.</p>",
    "description": """<h2>Un lavaplatos empotrado 80x44 que aguanta tu cocina real</h2>
<p>El <strong>lavaplatos empotrado 80x44</strong> con secador izquierdo es probablemente la medida más vendida del mercado chileno, y por buenas razones: combina cubeta amplia para ollas grandes con un secador funcional para los platos del almuerzo, todo en una huella que entra perfecto en muebles estándar de cocina chilenos.</p>
<p>Acero inoxidable de calidad, terminación pulida que se mantiene como nueva, espesor pensado para uso diario intensivo. No es de esos lavaplatos que se abollan con un golpe accidental o que pierden brillo después de meses de uso.</p>

<h3>Por qué este lavaplatos empotrado 80x44 es distinto</h3>
<ul>
  <li>Dimensiones 80 cm de ancho x 44 cm de fondo, ideales para muebles de cocina chilenos estándar.</li>
  <li>Cubeta amplia que acepta ollas grandes y sartenes sin tener que apilar.</li>
  <li>Secador izquierdo con canales de escurrido optimizados.</li>
  <li>Acero inoxidable resistente a manchas, golpes y agua dura.</li>
  <li>Empotrado clásico: se instala directo en el mesón sin necesidad de mueble especial.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Por qué el lavaplatos empotrado 80x44 es el favorito chileno</h3>
<p>La mayoría de los muebles de cocina chilenos vienen con cortes de 80 cm preparados para este tamaño exacto. Eso significa instalación directa sin tener que adaptar el mueble, sin obras adicionales y sin sorpresas. Si vas a renovar la cocina o reemplazar un lavaplatos viejo, esta es la opción de menor fricción y mayor compatibilidad.</p>
<p>Para complementar la instalación, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para cocina</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>

<h3>Instalación y compatibilidad</h3>
<p>Compatible con mesones de cocina estándar (granito, cuarzo, melamina). Recomendamos instalación con maestro con experiencia básica en montaje de lavaplatos. Vienen las clip y empaques necesarios para fijación e impermeabilización.</p>

<h3>Pensado para cocinas chilenas reales</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Despacho a todo Chile con respaldo Victtorino. Para complementar el conjunto, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para cocina y baño</a>.</p>
<p><strong>El lavaplatos empotrado 80x44 izquierdo es la opción más segura para una renovación de cocina sin complicaciones.</strong></p>""",
}

PROD_1582 = {  # #4 — Ducha Fija Difusor Muro (73+64=137 ventas)
    "action": "PUT", "woo_id": 1582,
    "focus": "ducha fija al muro",
    "meta_title": "Ducha Fija al Muro con Difusor ABS Cromado | Victtorino",
    "meta_desc": "Ducha fija al muro con difusor ABS cromado plateado. Instalación accesible, lluvia suave y resistente. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>La <strong>ducha fija al muro</strong> con difusor que renueva tu baño en una mañana. Lluvia suave, acabado cromado durable, instalación sin obras. Despacho a todo Chile.</p>",
    "description": """<h2>Una ducha fija al muro que cambia toda la sensación del baño</h2>
<p>La <strong>ducha fija al muro</strong> es la solución más limpia, estética y duradera cuando quieres una ducha que se vea ordenada, sin mangueras flexibles colgando, sin soportes que se desajustan, sin esa sensación de provisorio que tienen las teleduchas. Es la opción favorita para baños modernos y para hogares donde la simplicidad funcional importa.</p>
<p>Este modelo viene con difusor de plástico ABS reforzado con terminación cromada, que entrega una lluvia suave y pareja en cada uso. El acabado plateado se mantiene como nuevo después de meses de exposición al agua y al vapor del baño chileno.</p>

<h3>Por qué esta ducha fija al muro es distinta</h3>
<ul>
  <li>Difusor de ABS resistente que entrega lluvia uniforme sin gotas duras ni chorros aislados.</li>
  <li>Acabado cromado plateado que resiste manchas de agua dura y vapor permanente.</li>
  <li>Instalación al muro sin necesidad de obras: se conecta a la salida de agua estándar.</li>
  <li>Diseño limpio y compacto, ideal para baños modernos o renovados.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo elegir una ducha fija al muro</h3>
<p>Si tienes una ducha con cortina vieja, una teleducha que se desajusta, o un baño que quieres modernizar sin obras grandes, esta ducha fija al muro es probablemente el cambio de mayor impacto visual que puedes hacer con la menor inversión. Cinco minutos de gasfíter, y al día siguiente tu rutina de ducha se siente distinta.</p>
<p>Si vas a renovar más componentes, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>

<h3>Instalación accesible para tu maestro</h3>
<p>Compatible con instalaciones estándar del mercado chileno. Cualquier maestro gasfíter con experiencia básica la monta en menos de una hora. Vienen las conexiones y empaques necesarios.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería y accesorios de baño. Para complementar tu ducha, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>
<p><strong>Una ducha fija al muro bien elegida cambia la rutina diaria sin remodelar el baño.</strong></p>""",
}

PROD_2615 = {  # #5 — Basurero Pedal 5L Acero Inox (71 ventas)
    "action": "PUT", "woo_id": 2615,
    "focus": "basurero pedal baño",
    "meta_title": "Basurero Pedal Baño 5L Acero Inoxidable | Victtorino",
    "meta_desc": "Basurero pedal baño de 5 litros en acero inoxidable plateado. Apertura sin contacto, cierre suave. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>basurero pedal baño</strong> 5L que combina higiene y diseño. Acero inoxidable, apertura sin contacto, cierre silencioso. Despacho a todo Chile.</p>",
    "description": """<h2>Un basurero pedal baño que se ve bien y dura años</h2>
<p>El <strong>basurero pedal baño</strong> es uno de esos detalles que distinguen un baño cuidado de uno cualquiera. Apertura sin contacto, cierre suave que no hace ruido a media noche, acabado en acero inoxidable que sigue viéndose como nuevo después de meses de uso. La diferencia entre un basurero plástico cualquiera y este es como la diferencia entre una toalla de motel y una de hotel boutique: detalles que se sienten todos los días.</p>
<p>Esta versión de 5 litros es la medida perfecta para baños chilenos: ni tan grande que ocupe espacio innecesario, ni tan chico que haya que vaciarlo cada dos días.</p>

<h3>Por qué este basurero pedal baño es distinto</h3>
<ul>
  <li>Acero inoxidable resistente a manchas, huellas y humedad permanente del baño.</li>
  <li>Mecanismo de pedal silencioso: abre sin contacto y cierra sin golpe.</li>
  <li>Capacidad de 5 litros, ideal para baños familiares de uso diario.</li>
  <li>Cuerpo interior removible para vaciado y limpieza simple.</li>
  <li>Acabado plateado que combina con cualquier estilo de baño.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Higiene sin contacto: por qué importa</h3>
<p>En el baño, cada vez que tocas una superficie con las manos limpias antes de salir, pierdes un poco de lo que ganaste en el lavamanos. Un basurero pedal baño elimina ese punto de contacto crítico. Es la misma lógica de los dispensadores con sensor en baños profesionales, llevada al hogar.</p>
<p>Para complementar tu baño, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a> y <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a>.</p>

<h3>Pensado para hogares chilenos reales</h3>
<p>La humedad permanente del baño chileno (vapor de ducha, ventilación a veces limitada) deteriora rápido los basureros plásticos. El acero inoxidable de este modelo aguanta sin oxidarse ni decolorarse. Es de esos detalles que se ven cuando llevas un año usándolo, no el primer día.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en accesorios para baño y cocina. Despacho a todo Chile. Para complementar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/espejos/">espejos para baño</a>.</p>
<p><strong>Un buen basurero pedal baño es de esos detalles silenciosos que elevan toda la experiencia del espacio.</strong></p>""",
}

PROD_946 = {  # #6 — Plato Ducha Cuadrado 25cm Schwartz Negro (67 ventas)
    "action": "PUT", "woo_id": 946,
    "focus": "plato de ducha cuadrado",
    "meta_title": "Plato de Ducha Cuadrado 25cm Schwartz Negro | Victtorino",
    "meta_desc": "Plato de ducha cuadrado 25 cm acabado Schwartz negro. Acero inoxidable, lluvia tipo cascada. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>plato de ducha cuadrado</strong> 25 cm en negro Schwartz que transforma cualquier ducha en una experiencia tipo hotel boutique. Acero inoxidable durable. Despacho a todo Chile.</p>",
    "description": """<h2>Un plato de ducha cuadrado que convierte tu ducha en un ritual</h2>
<p>El <strong>plato de ducha cuadrado</strong> de 25 cm en acabado Schwartz negro es de esos elementos que distinguen un baño común de un baño con identidad. Es el detalle que ves cuando entras a una suite de hotel y dices "este baño está bien pensado". Lluvia abundante tipo cascada, presencia visual marcada, acabado oscuro contemporáneo que rompe con el clásico cromado plateado.</p>
<p>El acero inoxidable con terminación negra Schwartz no es solo estética: es resistencia real a las manchas de agua dura, al vapor permanente y al uso diario. Y la geometría cuadrada le da una elegancia arquitectónica que el plato redondo común no entrega.</p>

<h3>Por qué este plato de ducha cuadrado es distinto</h3>
<ul>
  <li>Dimensiones 25x25 cm, óptimo para ducha individual sin saturar el espacio visual.</li>
  <li>Acabado Schwartz negro: contemporáneo, resistente y distinto al cromado clásico.</li>
  <li>Acero inoxidable de espesor que aguanta golpes accidentales sin deformarse.</li>
  <li>Salida de agua tipo cascada uniforme, sin chorros aislados ni gotas duras.</li>
  <li>Compatible con instalaciones estándar de ducha chilenas.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>El negro Schwartz como tendencia</h3>
<p>Los acabados en negro mate o brillante son la tendencia más fuerte en grifería de baño de los últimos años. No es solo moda: el negro disimula mejor las manchas de agua dura, combina con cualquier estilo de baño y entrega presencia visual sin necesidad de obras grandes. Un plato de ducha cuadrado negro en un baño blanco clásico se ve increíble; en un baño moderno también.</p>
<p>Si estás renovando todo el conjunto, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>

<h3>Instalación accesible</h3>
<p>Se conecta al brazo de ducha estándar (rosca 1/2). Cualquier maestro gasfíter con experiencia básica lo monta en 15 minutos. Para complementar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Despacho a todo Chile.</p>
<p><strong>Convierte tu ducha diaria en algo que esperas con ganas.</strong> Un plato de ducha cuadrado negro Schwartz cambia más cosas de las que parece.</p>""",
}

PROD_2963 = {  # #7 — Lavaplatos 80x44 Inox Sec.Derecho (66 ventas)
    "action": "PUT", "woo_id": 2963,
    "focus": "lavaplatos 80x44 inoxidable",
    "meta_title": "Lavaplatos 80x44 Inoxidable Secador Derecho | Victtorino",
    "meta_desc": "Lavaplatos 80x44 inoxidable con secador derecho. Acero durable, dimensiones estándar para cocinas chilenas. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>lavaplatos 80x44 inoxidable</strong> con secador derecho que tu cocina chilena necesita. Acero durable, cubeta amplia, instalación directa. Despacho a todo Chile.</p>",
    "description": """<h2>El lavaplatos 80x44 inoxidable más versátil del mercado chileno</h2>
<p>El <strong>lavaplatos 80x44 inoxidable</strong> con secador derecho es probablemente la combinación más vendida y favorita en cocinas chilenas, y por una razón muy simple: 80 cm es exactamente el ancho de los muebles de cocina más comunes del mercado, y 44 cm de fondo entra perfecto bajo cualquier mesón estándar. Compatibilidad total, instalación directa, sin obras de adaptación.</p>
<p>Acero inoxidable de espesor pensado para uso intensivo, terminación pulida que se mantiene como nueva después de meses de lavados diarios. La cubeta acepta ollas grandes y sartenes anchas sin esfuerzo.</p>

<h3>Por qué este lavaplatos 80x44 inoxidable es distinto</h3>
<ul>
  <li>Acero inoxidable resistente a manchas de agua dura, productos químicos y golpes.</li>
  <li>Dimensiones 80x44 cm: la medida más estándar en muebles de cocina chilenos.</li>
  <li>Secador derecho con canales de escurrido optimizados para escurrido natural.</li>
  <li>Cubeta amplia que acepta ollas para 4-6 personas sin tener que apilar.</li>
  <li>Acabado pulido que se mantiene como nuevo con limpieza básica.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>La medida 80x44: el estándar chileno</h3>
<p>La mayoría de las cocinas chilenas se diseñan con muebles modulares de 80 cm. Eso convierte al lavaplatos 80x44 inoxidable en la opción más segura cuando renuevas: no tienes que adaptar el mueble, no tienes que cortar mesón nuevo, no tienes sorpresas. Si tu cocina actual ya tiene un lavaplatos de esta medida, el reemplazo es directo.</p>
<p>Si vas a complementar la cocina, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para cocina</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>

<h3>Instalación y compatibilidad</h3>
<p>Empotrado clásico que se instala directo sobre el mesón existente. Compatible con granito, cuarzo y melamina. Cualquier maestro con experiencia básica lo cambia en menos de dos horas.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Despacho a todo Chile. Para complementar tu cocina, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios</a>.</p>
<p><strong>El lavaplatos 80x44 inoxidable es la opción más segura para una renovación de cocina sin imprevistos.</strong></p>""",
}

PROD_1261 = {  # #8 — Lavaplatos 100x44 Izquierdo (66 ventas)
    "action": "PUT", "woo_id": 1261,
    "focus": "lavaplatos empotrado 100x44",
    "meta_title": "Lavaplatos Empotrado 100x44 Secador Izquierdo | Victtorino",
    "meta_desc": "Lavaplatos empotrado 100x44 cm con secador izquierdo. Cubeta amplia, acero inoxidable durable. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>El <strong>lavaplatos empotrado 100x44</strong> con secador izquierdo. Espacio extra para cocinas familiares, acero durable. Despacho a todo Chile.</p>",
    "description": """<h2>Un lavaplatos empotrado 100x44 cuando tu cocina pide más espacio</h2>
<p>El <strong>lavaplatos empotrado 100x44</strong> con secador izquierdo es para cocinas donde el lavado es intensivo: familias grandes, ollas industriales, ritmo diario de varios cubiertos. Los 20 cm extra respecto al 80x44 hacen una diferencia enorme: aceptas más loza, escurres más cómodo, lavas más rápido.</p>
<p>Acero inoxidable de espesor durable, terminación pulida resistente y geometría pensada para que el agua escurra sin acumularse. Si tu cocina tiene espacio para esta medida, es la decisión correcta.</p>

<h3>Por qué este lavaplatos empotrado 100x44 es distinto</h3>
<ul>
  <li>Dimensiones 100x44 cm: amplio para cocinas familiares activas.</li>
  <li>Cubeta de mayor capacidad, acepta ollas grandes y bandejas de horno.</li>
  <li>Secador izquierdo con canales optimizados para escurrido natural.</li>
  <li>Acero inoxidable resistente a manchas, golpes y productos químicos.</li>
  <li>Compatible con muebles de cocina estándar con corte de 100 cm.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo elegir un lavaplatos empotrado 100x44</h3>
<p>Si tu familia es de 4 o más personas, si cocinas seguido con ollas grandes, si te molesta tener que apilar loza en un lavaplatos chico, esta es la respuesta. Los 20 cm extra del 100x44 sobre el 80x44 estándar transforman la experiencia diaria.</p>
<p>Si vas a renovar más componentes de la cocina, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para cocina</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>

<h3>Instalación y compatibilidad</h3>
<p>Requiere mueble de cocina con corte de 100 cm o un mueble modular más amplio. Cualquier maestro con experiencia básica lo cambia en una visita. Compatible con mesones de granito, cuarzo y melamina.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en cocina y baño. Despacho a todo Chile. Para complementar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para cocina</a>.</p>
<p><strong>Más espacio, mejor escurrido, lavados más rápidos. Un lavaplatos empotrado 100x44 cambia el ritmo de la cocina familiar.</strong></p>""",
}

PROD_NEW_LLAVE_LAVADORA = {  # #9 — Llave Doble Lavadora Jardín 2 Salidas (65 ventas) — IMPORT
    "action": "POST", "ml_id": "MLC1307538393",
    "cat_destino": "Griferia",
    "focus": "llave doble lavadora",
    "meta_title": "Llave Doble Lavadora Jardín 2 Salidas | Victtorino",
    "meta_desc": "Llave doble lavadora con 2 salidas para conectar simultáneamente lavadora y manguera de jardín. Bronce durable. Despacho a todo Chile. Victtorino.",
    "short_desc": "<p>La <strong>llave doble lavadora</strong> con 2 salidas que evita andar conectando y desconectando. Bronce durable, instalación directa. Despacho a todo Chile.</p>",
    "description": """<h2>Una llave doble lavadora que simplifica la rutina de la casa</h2>
<p>La <strong>llave doble lavadora</strong> con 2 salidas es uno de esos accesorios que parecen menores pero terminan ahorrando tiempo todos los días. Si tienes la lavadora conectada a la misma llave de jardín y quieres usar la manguera para regar, lavar el patio o llenar una balde, sabes el lío: desconectar la lavadora, conectar la manguera, volver a conectar la lavadora cuando terminas. Con esta llave doble, las dos cosas están siempre conectadas y solo abres la que necesitas.</p>
<p>Bronce de calidad, mecanismos durables, conexiones estándar. Es una de esas mejoras que pagan su costo en pocos meses por el simple ahorro de tiempo.</p>

<h3>Por qué esta llave doble lavadora es distinta</h3>
<ul>
  <li>Dos salidas independientes con mando de apertura/cierre separado.</li>
  <li>Bronce resistente a la corrosión del exterior y al agua dura.</li>
  <li>Conexiones estándar 3/4 para manguera y 1/2 para lavadora.</li>
  <li>Diseño compacto que no estorba ni acumula suciedad.</li>
  <li>Compatible con instalaciones chilenas estándar de patio y lavandería.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Para quién es esta llave doble lavadora</h3>
<p>Para hogares con lavandería en el patio o cerca del jardín, para casas donde la lavadora comparte la salida de agua con la manguera de riego, o para departamentos con balcón donde la lavadora está al lado del lavadero. Una solución pequeña que mejora la rutina diaria sin obras grandes.</p>
<p>Si vas a renovar más grifería del hogar, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño y cocina</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios</a>.</p>

<h3>Instalación accesible</h3>
<p>Cualquier maestro gasfíter con experiencia básica la instala en 15 minutos. Solo necesitas cerrar el paso, cambiar la llave simple por la doble, y conectar manguera + lavadora. Sin obras, sin polvo, sin sorpresas.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería y accesorios. Despacho a todo Chile. Para complementar la lavandería, mira también nuestros <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>
<p><strong>Una llave doble lavadora es de esos pequeños cambios que se notan todos los días.</strong></p>""",
}

PROD_1235 = {  # #11 — Llave Lavatorio Temporizada Al Muro Larga (50 ventas)
    "action": "PUT", "woo_id": 1235,
    "focus": "llave temporizada baño",
    "meta_title": "Llave Temporizada Baño al Muro Larga | Victtorino",
    "meta_desc": "Llave temporizada baño al muro versión larga. Ahorro de agua automático, ideal para baños públicos e institucionales. Despacho a todo Chile.",
    "short_desc": "<p>La <strong>llave temporizada baño</strong> al muro larga, ideal para baños públicos, oficinas y locales. Ahorro automático de agua, durabilidad para uso intensivo. Despacho a todo Chile.</p>",
    "description": """<h2>Una llave temporizada baño que paga su costo en agua ahorrada</h2>
<p>La <strong>llave temporizada baño</strong> al muro en versión larga es esa pieza que distingue un baño público bien diseñado de uno cualquiera. Apertura con un botón firme, descarga automática durante el tiempo exacto necesario, cierre seguro que no depende de que el usuario se acuerde de cerrar la llave. Adiós a los grifos quedados abiertos, adiós al desperdicio de agua, adiós a la cuenta del agua creciendo por gente que olvidó cerrar.</p>
<p>Material durable, mecanismo de calidad, terminación cromada plateada que aguanta el uso intensivo de oficinas, restaurantes, colegios, gimnasios y baños institucionales.</p>

<h3>Por qué esta llave temporizada baño es distinta</h3>
<ul>
  <li>Mecanismo de cierre automático calibrado para ciclos de 5-8 segundos.</li>
  <li>Acabado cromado plateado resistente a manchas, huellas y vandalismo leve.</li>
  <li>Versión larga: extiende el flujo desde el muro, ideal cuando el lavamanos no está pegado a la pared.</li>
  <li>Compatible con instalaciones estándar chilenas.</li>
  <li>Diseño pensado para baño público con alto flujo de usuarios.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Para qué espacios es ideal una llave temporizada baño</h3>
<p>Oficinas con baño compartido, restaurantes, cafés, colegios, gimnasios, locales comerciales, estaciones de servicio y baños institucionales en general. Cualquier baño con flujo de usuarios donde el desperdicio de agua sea una preocupación real. También funciona excelente en baños de visitas de hogares donde no se confía en que todos cierren bien la llave.</p>
<p>Si vas a equipar un baño profesional completo, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a>.</p>

<h3>El ROI de una llave temporizada baño</h3>
<p>El cálculo simple: una llave común quedada abierta 5 minutos al día gasta más en agua en un año que el costo de una llave temporizada. En baños públicos con mucho flujo, el retorno es de meses, no años. Es una de las inversiones más rentables que puede hacer un local en su baño.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería para baño profesional. Despacho a todo Chile. Para complementar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>
<p><strong>Una llave temporizada baño es de esas decisiones que ahorran dinero todos los días.</strong></p>""",
}


PRODUCTOS = [PROD_1814, PROD_2734, PROD_NEW_LAVAPLATOS_80_IZQ, PROD_1582, PROD_2615,
             PROD_946, PROD_2963, PROD_1261, PROD_NEW_LLAVE_LAVADORA, PROD_1235]


def woo_request(method, path, **kwargs):
    url = f"{WC}/wp-json/wc/v3{path}"
    kwargs.setdefault("timeout", 180)
    kwargs.setdefault("params", {}).update(P)
    for n in range(1, 5):
        try:
            r = requests.request(method, url, **kwargs)
            if r.status_code == 503:
                time.sleep(8 * n)
                continue
            if r.status_code >= 400:
                print(f"    HTTP {r.status_code}: {r.text[:200]}")
                return None
            return r.json()
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            print(f"    RED {type(e).__name__}; retry in {4*n}s")
            time.sleep(4 * n)
    return None


def aplicar_put(prod):
    body = {
        "name": prod.get("name"),  # opcional
        "description": prod["description"],
        "short_description": prod["short_desc"],
        "meta_data": [
            {"key": "rank_math_title", "value": prod["meta_title"]},
            {"key": "rank_math_description", "value": prod["meta_desc"]},
            {"key": "rank_math_focus_keyword", "value": prod["focus"]},
        ],
    }
    body = {k: v for k, v in body.items() if v is not None}
    return woo_request("PUT", f"/products/{prod['woo_id']}", json=body)


def aplicar_post(prod):
    # Cargar IDs categorias
    cats = woo_request("GET", "/products/categories", params={"per_page": 100})
    cat_id_por_nombre = {c["name"]: c["id"] for c in cats}
    # Detalle ML
    item = requests.get(f"https://api.mercadolibre.com/items/{prod['ml_id']}",
                        headers=ML_HEAD, timeout=30).json()
    titulo = item.get("title", "")
    precio = item.get("price")
    stock = int(item.get("available_quantity") or 0)
    pictures = [p["url"] for p in item.get("pictures", []) if p.get("url")]
    images_payload = [{"src": u, "alt": (titulo if i == 0 else f"{titulo} - foto {i+1}")[:120]}
                      for i, u in enumerate(pictures)]
    sku = f"ML-{prod['ml_id']}"
    # Idempotencia
    existente = woo_request("GET", "/products", params={"sku": sku})
    if existente:
        print(f"  YA EXISTE Woo {existente[0]['id']}, hago PUT en su lugar")
        prod["woo_id"] = existente[0]["id"]
        return aplicar_put(prod)
    body = {
        "name": titulo,
        "slug": slugify(titulo),
        "type": "simple",
        "status": "draft",
        "regular_price": str(int(precio)) if precio else "",
        "manage_stock": True,
        "stock_quantity": stock,
        "description": prod["description"],
        "short_description": prod["short_desc"],
        "sku": sku,
        "categories": [{"id": cat_id_por_nombre[prod["cat_destino"]]}],
        "images": images_payload,
        "meta_data": [
            {"key": "rank_math_title", "value": prod["meta_title"]},
            {"key": "rank_math_description", "value": prod["meta_desc"]},
            {"key": "rank_math_focus_keyword", "value": prod["focus"]},
        ],
    }
    return woo_request("POST", "/products", json=body)


print(f"Aplicando SEO premium INDIVIDUAL a {len(PRODUCTOS)} productos (Lote 1)\n")
resultados = []
for idx, prod in enumerate(PRODUCTOS, start=1):
    accion = prod["action"]
    ident = prod.get("woo_id") or prod.get("ml_id")
    print(f"({idx}/{len(PRODUCTOS)}) {accion} {ident} focus=\"{prod['focus']}\"")
    res = aplicar_put(prod) if accion == "PUT" else aplicar_post(prod)
    if res:
        plain = re.sub(r"<[^>]+>", " ", res.get("description", ""))
        pal = len(plain.split())
        fk_count = plain.lower().count(prod["focus"].lower())
        h2 = re.findall(r"<h2[^>]*>([^<]+)</h2>", res.get("description", ""))
        h2_fk = "SI" if any(prod["focus"].lower() in h.lower() for h in h2) else "no"
        meta_d = next((m["value"] for m in res.get("meta_data", []) if m["key"] == "rank_math_description"), "")
        meta_fk = "SI" if prod["focus"].lower() in meta_d.lower() else "no"
        links = res.get("description", "").count('href="')
        print(f"     OK Woo {res['id']} status={res.get('status')} palabras={pal} fk_count={fk_count} H2_fk={h2_fk} meta_fk={meta_fk} links={links}")
        resultados.append({"id": res["id"], "ok": True, "pal": pal, "fk_count": fk_count,
                           "focus": prod["focus"], "name": res.get("name", "")[:50]})
    else:
        print(f"     FALLO")
        resultados.append({"id": ident, "ok": False})
    time.sleep(2)

print("\n" + "=" * 70)
print(f"RESUMEN: {sum(1 for r in resultados if r.get('ok'))}/{len(PRODUCTOS)}")
print("=" * 70)
for r in resultados:
    if r.get("ok"):
        print(f"  {r['id']:5} {r['pal']:4}pal fk{r['fk_count']:2}x \"{r['focus']:25}\" {r['name']}")
    else:
        print(f"  {r['id']} FALLO")

with open(r"C:\Users\dell\victtorino\seo_top10_resultado.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
