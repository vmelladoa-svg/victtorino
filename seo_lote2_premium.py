"""
Lote 2 — SEO premium INDIVIDUAL para los siguientes 8 productos del top vendido ML C3.
Incluye 1 import nuevo (lavaplatos 100x44 derecho).
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
# 8 PRODUCTOS DEL LOTE 2
# ============================================================

PROD_3009 = {  # #12 — Barra Soporte Ducha 65cm Deslizable (49 ventas)
    "action": "PUT", "woo_id": 3009,
    "focus": "barra ducha deslizable",
    "meta_title": "Barra de Ducha Deslizable 65cm Acero Inox | Victtorino",
    "meta_desc": "Barra ducha deslizable de 65 cm en acero inoxidable. Soporte ajustable para teleducha, altura regulable para toda la familia. Despacho a todo Chile.",
    "short_desc": "<p>La <strong>barra ducha deslizable</strong> de 65 cm que adapta la altura de la teleducha a cada persona de la familia. Acero inoxidable durable, instalación directa. Despacho a todo Chile.</p>",
    "description": """<h2>Una barra ducha deslizable que se adapta a toda la familia</h2>
<p>La <strong>barra ducha deslizable</strong> es de esos accesorios que cambian la rutina de ducha sin que te des cuenta: el soporte sube cuando se baña papá, baja cuando se ducha el niño, queda intermedio para la rutina diaria. Lo que parece un detalle menor termina ahorrando frustración todos los días.</p>
<p>Esta barra de 65 cm en acero inoxidable cromado entrega un rango de altura ideal para hogares chilenos estándar. El soporte deslizable se ajusta firmemente sin requerir herramientas, y el acabado pulido resiste el vapor permanente y el agua dura sin oxidarse.</p>

<h3>Por qué esta barra ducha deslizable es distinta</h3>
<ul>
  <li>Longitud de 65 cm: rango óptimo para techos chilenos estándar.</li>
  <li>Acero inoxidable resistente a la corrosión del baño húmedo.</li>
  <li>Mecanismo de ajuste con un solo gesto, sin tornillos ni herramientas.</li>
  <li>Compatible con la mayoría de teleduchas estándar del mercado chileno.</li>
  <li>Acabado plateado pulido que combina con cualquier estilo de baño.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Para quién es esta barra ducha deslizable</h3>
<p>Para hogares con más de una persona usando la misma ducha y distintas alturas. Para casas con abuelos donde la teleducha sentada es necesaria. Para padres que quieren que sus hijos chicos puedan ducharse solos cómodamente. Una barra ducha deslizable resuelve todos esos escenarios con una sola pieza.</p>
<p>Si vas a renovar la grifería del shower, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>

<h3>Instalación accesible</h3>
<p>Se fija al muro con dos puntos de anclaje incluidos. Tornillos y tarugos vienen en la caja. Cualquier maestro con experiencia básica la monta en 20 minutos. Si vas a complementar la seguridad del shower, mira también nuestras <a href="https://victtorino.cl/categoria-producto/agarraderas-y-barras-para-bano/">agarraderas y barras de seguridad</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en accesorios para baño. Despacho a todo Chile.</p>
<p><strong>Una barra ducha deslizable es la solución más simple y elegante para que la ducha quede cómoda para todos en casa.</strong></p>""",
}

PROD_2578 = {  # #13 — Llave Temporizada Urinario (41 ventas)
    "action": "PUT", "woo_id": 2578,
    "focus": "llave temporizada urinario",
    "meta_title": "Llave Temporizada Urinario Plateado | Victtorino",
    "meta_desc": "Llave temporizada urinario con descarga automática. Ahorro de agua e higiene para baños públicos e institucionales. Despacho a todo Chile.",
    "short_desc": "<p>La <strong>llave temporizada urinario</strong> que ahorra agua automáticamente en cada uso. Ideal para oficinas, restaurantes, colegios y baños institucionales. Despacho a todo Chile.</p>",
    "description": """<h2>Una llave temporizada urinario que ahorra agua todos los días</h2>
<p>La <strong>llave temporizada urinario</strong> es esa pieza que distingue un baño público profesional de uno descuidado. Apertura con un botón firme, descarga calibrada al tiempo exacto necesario, cierre automático que no depende de que el usuario recuerde. Adiós a urinarios con la llave abierta toda la tarde, adiós a goteos permanentes, adiós a la cuenta de agua creciendo sin explicación.</p>
<p>Material durable, mecanismo de calidad, terminación plateada cromada que aguanta el uso intensivo de baños institucionales con flujo alto. Una pieza pensada para resistir, no para reemplazarse cada año.</p>

<h3>Por qué esta llave temporizada urinario es distinta</h3>
<ul>
  <li>Mecanismo de cierre automático calibrado para descarga eficiente.</li>
  <li>Acabado plateado cromado resistente a manchas, huellas y vandalismo leve.</li>
  <li>Compatible con instalaciones estándar chilenas para urinarios institucionales.</li>
  <li>Diseño pensado para baño público con alto flujo de usuarios diario.</li>
  <li>Materiales internos que aguantan el agua dura y la cloración del agua potable.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Dónde es indispensable una llave temporizada urinario</h3>
<p>Oficinas con baño público, restaurantes, cafés, colegios, universidades, gimnasios, estaciones de servicio, locales comerciales, centros médicos y cualquier espacio con baño compartido. En estos contextos, una llave común queda abierta más veces de las que uno se imagina, y el costo en agua se acumula silenciosamente. La llave temporizada urinario es la solución más limpia.</p>
<p>Si vas a equipar un baño profesional completo, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/wc-e-inodoros/">WC e inodoros</a>.</p>

<h3>Instalación accesible</h3>
<p>Compatible con la mayoría de los urinarios institucionales chilenos. Cualquier gasfíter con experiencia básica la instala en 30 minutos. Para complementar el equipamiento del baño público, mira también nuestros <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería para baños profesionales e institucionales. Despacho a todo Chile.</p>
<p><strong>Una llave temporizada urinario paga su costo en agua ahorrada en pocos meses.</strong></p>""",
}

PROD_NEW_LAVAPLATOS_100_DER = {  # #14 — Lavaplatos 100x44 Derecho (36 ventas) — IMPORT
    "action": "POST", "ml_id": "MLC1306255938",
    "cat_destino": "Lavaplatos",
    "focus": "lavaplatos empotrado 100x44 derecho",
    "meta_title": "Lavaplatos Empotrado 100x44 Secador Derecho | Victtorino",
    "meta_desc": "Lavaplatos empotrado 100x44 cm con secador derecho. Cubeta amplia para cocinas familiares, acero inoxidable durable. Despacho a todo Chile.",
    "short_desc": "<p>El <strong>lavaplatos empotrado 100x44 derecho</strong> para cocinas familiares activas. Espacio amplio, acero durable, instalación estándar. Despacho a todo Chile.</p>",
    "description": """<h2>Un lavaplatos empotrado 100x44 derecho para cocinas familiares</h2>
<p>El <strong>lavaplatos empotrado 100x44 derecho</strong> es la opción ideal cuando tu cocina pide más espacio del que entrega el 80x44 estándar. Los 20 cm extra hacen una diferencia notable: aceptas más loza, escurres más cómodo, ollas grandes entran sin esfuerzo. La versión con secador derecho es la elección natural cuando la llave queda a la izquierda y necesitas el escurridor del otro lado.</p>
<p>Acero inoxidable de espesor durable, terminación pulida resistente, geometría pensada para que el agua escurra de forma natural hacia la cubeta. La diferencia entre un lavaplatos cualquiera y uno bien diseñado se nota en el segundo año de uso.</p>

<h3>Por qué este lavaplatos empotrado 100x44 derecho es distinto</h3>
<ul>
  <li>Dimensiones 100x44 cm: amplio para cocinas familiares activas y ollas grandes.</li>
  <li>Secador derecho con canales optimizados para escurrido natural sin acumulación.</li>
  <li>Cubeta de mayor capacidad que el 80x44 estándar — diferencia notable en el día a día.</li>
  <li>Acero inoxidable resistente a manchas, golpes y agua dura.</li>
  <li>Compatible con muebles de cocina chilenos estándar con corte de 100 cm.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo elegir el secador derecho</h3>
<p>Depende de dónde está la llave de tu cocina. Si la grifería queda a la izquierda, el lavaplatos empotrado 100x44 derecho es la elección lógica: lavas, escurres y dejas la loza a la derecha sin chocar con la llave. Si tu llave está a la derecha, el modelo izquierdo es el indicado. Pequeño detalle, gran diferencia ergonómica todos los días.</p>
<p>Para complementar la cocina, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para cocina</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>

<h3>Instalación y compatibilidad</h3>
<p>Empotrado clásico que se instala directo sobre mesón con corte de 100 cm. Compatible con granito, cuarzo y melamina. Cualquier maestro con experiencia básica lo monta en una visita.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Despacho a todo Chile. Para complementar tu cocina, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios</a>.</p>
<p><strong>El lavaplatos empotrado 100x44 derecho es la decisión inteligente cuando tu cocina pide más espacio.</strong></p>""",
}

PROD_3117 = {  # #15 — Llave Monomando Lavatorio Modern (34 ventas)
    "action": "PUT", "woo_id": 3117,
    "focus": "llave monomando lavatorio",
    "meta_title": "Llave Monomando Lavatorio Modern Cepillado | Victtorino",
    "meta_desc": "Llave monomando lavatorio Modern en acabado cepillado plateado. Control de temperatura y caudal con una sola palanca. Despacho a todo Chile.",
    "short_desc": "<p>La <strong>llave monomando lavatorio</strong> Modern que combina diseño contemporáneo con la simplicidad de una sola palanca. Acabado cepillado plateado durable. Despacho a todo Chile.</p>",
    "description": """<h2>Una llave monomando lavatorio que se siente al primer uso</h2>
<p>La <strong>llave monomando lavatorio</strong> Modern combina diseño contemporáneo con la simplicidad funcional de una sola palanca que controla temperatura y caudal en un mismo gesto. Acabado cepillado plateado que esconde las huellas digitales y las marcas de agua dura, dándole al baño esa sensación de cuidado permanente que las llaves cromadas clásicas pierden con los meses.</p>
<p>Mecanismo cerámico de larga duración: nada de goteos prematuros, nada de juntas tóricas resecas en el primer año. La diferencia entre una llave monomando lavatorio que aguanta y una que toca reparar a los seis meses está justo en este componente.</p>

<h3>Por qué esta llave monomando lavatorio es distinta</h3>
<ul>
  <li>Mecanismo cerámico de larga duración: sin goteos prematuros ni reparaciones frecuentes.</li>
  <li>Acabado cepillado plateado que disimula manchas de agua dura y huellas.</li>
  <li>Control de temperatura y caudal con un solo gesto, ergonomía superior al doble manilla.</li>
  <li>Compatible con instalaciones estándar del mercado chileno.</li>
  <li>Diseño contemporáneo que combina con baños modernos, nórdicos o clásicos renovados.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Por qué monomando y no doble manilla</h3>
<p>El monomando se impuso en grifería de baño moderna por una razón simple: en un solo gesto controlas todo. Abrir el agua, ajustar la temperatura, cerrar — todo con la palanca. La doble manilla obliga a ajustar dos válvulas para llegar a la temperatura correcta, gasta más agua mientras encuentras el punto, y se ve más anticuada. Una llave monomando lavatorio bien hecha es una decisión que se siente cada vez que te lavas las manos.</p>
<p>Si vas a renovar todo el conjunto del baño, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/lavamanos/">lavamanos</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Instalación accesible</h3>
<p>Compatible con instalaciones estándar de lavamanos chilenos. Cualquier maestro gasfíter con experiencia básica la monta en menos de una hora. Para complementar el baño, mira también nuestros <a href="https://victtorino.cl/categoria-producto/espejos/">espejos para baño</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería de baño. Despacho a todo Chile.</p>
<p><strong>Una llave monomando lavatorio bien elegida cambia la rutina del baño sin remodelar.</strong></p>""",
}

PROD_2739 = {  # #16 — Dispensador Papel Higiénico Acrílico (31 ventas)
    "action": "PUT", "woo_id": 2739,
    "focus": "dispensador papel higiénico",
    "meta_title": "Dispensador Papel Higiénico Acrílico Plateado | Victtorino",
    "meta_desc": "Dispensador papel higiénico acrílico con tapa. Capacidad para rollo industrial, ideal para baños comerciales. Despacho a todo Chile.",
    "short_desc": "<p>El <strong>dispensador papel higiénico</strong> acrílico que ordena visualmente cualquier baño comercial o público. Capacidad rollo industrial, instalación directa. Despacho a todo Chile.</p>",
    "description": """<h2>Un dispensador papel higiénico que distingue un baño profesional</h2>
<p>El <strong>dispensador papel higiénico</strong> acrílico con tapa es esa pieza que distingue un baño público bien diseñado de uno que solo tiene un rollo apoyado en el lavamanos. No es solo estética: protege el papel de la humedad y del polvo, controla el consumo, evita que se desperdicien rollos, y le da al baño esa sensación de cuidado que los usuarios notan aunque no la mencionen.</p>
<p>Diseñado para rollo industrial de mayor capacidad, este dispensador resuelve la logística de baños con alto flujo: oficinas, restaurantes, locales comerciales, colegios. Materiales pensados para uso intensivo durante años.</p>

<h3>Por qué este dispensador papel higiénico es distinto</h3>
<ul>
  <li>Acrílico transparente que permite ver cuánto papel queda sin abrir la tapa.</li>
  <li>Capacidad para rollo industrial: menos recambios, menos logística diaria.</li>
  <li>Tapa con cierre que protege el papel de humedad, polvo y manipulación.</li>
  <li>Diseño compacto que se integra a cualquier estilo de baño.</li>
  <li>Compatible con instalaciones estándar al muro, fijación incluida.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Dónde es indispensable un dispensador papel higiénico industrial</h3>
<p>Oficinas con baño compartido entre 5+ personas, restaurantes y cafés, colegios, universidades, gimnasios, estaciones de servicio, locales comerciales con baño público, centros médicos y baños de eventos. En estos contextos, un dispensador papel higiénico no es opcional — es la única forma de controlar consumo y mantener higiene de forma profesional.</p>
<p>Si vas a equipar un baño profesional completo, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Instalación accesible</h3>
<p>Se fija al muro con dos tornillos. Cualquier persona lo instala en 15 minutos con un taladro básico. Vienen las fijaciones incluidas. Para complementar el equipamiento, mira también nuestra <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño profesional</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en accesorios para baño comercial y hogareño. Despacho a todo Chile.</p>
<p><strong>Un dispensador papel higiénico bien elegido eleva la experiencia del baño y ahorra dinero en consumo de papel.</strong></p>""",
}

PROD_2783 = {  # #17 — Brazo Plato Ducha 30cm Entrada Flexible (30 ventas)
    "action": "PUT", "woo_id": 2783,
    "focus": "brazo de ducha al muro",
    "meta_title": "Brazo de Ducha al Muro 30cm Acero Inoxidable | Victtorino",
    "meta_desc": "Brazo de ducha al muro de 30 cm con entrada flexible. Acero inoxidable cromado durable, compatible con duchas estándar. Despacho a todo Chile.",
    "short_desc": "<p>El <strong>brazo de ducha al muro</strong> de 30 cm que conecta tu plato de ducha al muro con elegancia. Acero inoxidable durable, instalación accesible. Despacho a todo Chile.</p>",
    "description": """<h2>Un brazo de ducha al muro que sostiene tu plato con elegancia</h2>
<p>El <strong>brazo de ducha al muro</strong> de 30 cm es la pieza que conecta la salida de agua del muro con el plato de ducha. Parece simple — es solo un tubo cromado — pero la calidad de esta pieza define la postura de toda la ducha: si está mal hecho, el plato se inclina con el tiempo, gotea por la rosca, o se oxida en la unión. Si está bien hecho, ni te das cuenta de que existe.</p>
<p>Acero inoxidable con terminación cromada plateada, entrada flexible que permite ajustar el ángulo del plato sin tener que mover toda la instalación. Diseño compacto que se ve elegante con cualquier plato de ducha moderno.</p>

<h3>Por qué este brazo de ducha al muro es distinto</h3>
<ul>
  <li>Acero inoxidable resistente a la corrosión del vapor permanente del baño.</li>
  <li>Entrada flexible que permite ajustar el ángulo de salida del plato.</li>
  <li>Acabado cromado plateado uniforme que combina con cualquier grifería.</li>
  <li>Longitud de 30 cm: óptima para distancias estándar muro-plato chilenas.</li>
  <li>Compatible con instalaciones estándar (rosca 1/2 muro, rosca 1/2 plato).</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Cuándo cambiar el brazo de ducha al muro</h3>
<p>Si el plato de ducha se ve inclinado o ladeado, si notas gotas saliendo de la unión brazo-muro, si el brazo viejo se ve oxidado o decolorado, o si simplemente vas a renovar el plato de ducha por uno más grande, es buen momento para cambiar también el brazo. Es una pieza barata, pero su estado condiciona toda la estética visible del shower.</p>
<p>Si vas a renovar todo el conjunto, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a> y <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>

<h3>Instalación accesible</h3>
<p>Cualquier maestro gasfíter con experiencia básica lo cambia en 15 minutos. Cierras el paso de agua, desenroscas el brazo viejo, atornillas el nuevo con teflón. Sin obras, sin polvo. Para complementar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Despacho a todo Chile.</p>
<p><strong>Un buen brazo de ducha al muro es esa pieza silenciosa que sostiene toda la experiencia de la ducha.</strong></p>""",
}

PROD_3084 = {  # #18 — Dispensador Jabón Täumm Pared (30 ventas)
    "action": "PUT", "woo_id": 3084,
    "focus": "dispensador jabón pared",
    "meta_title": "Dispensador Jabón Pared Täumm 500ml | Victtorino",
    "meta_desc": "Dispensador jabón pared Täumm de 500ml en plástico blanco. Higiene moderna sin botellas comerciales rompiendo la estética. Despacho a todo Chile.",
    "short_desc": "<p>El <strong>dispensador jabón pared</strong> Täumm que elimina las botellas comerciales del lavamanos. Diseño compacto, capacidad 500ml, recargable. Despacho a todo Chile.</p>",
    "description": """<h2>Un dispensador jabón pared que ordena visualmente todo el baño</h2>
<p>El <strong>dispensador jabón pared</strong> es de esos detalles que separan un baño cuidado de uno descuidado. Si has visto baños de hoteles boutique, oficinas modernas o restaurantes bien diseñados, sabes que ninguno tiene la botella plástica del jabón comercial sobre el lavamanos. Tienen un dispensador discreto en la pared, integrado a la estética, recargable con cualquier jabón a granel.</p>
<p>Este modelo Täumm de 500 ml en plástico blanco resistente entrega dosis controlada con una pulsada, sin goteos en el lavamanos, sin restos pegajosos en la botella, sin la imagen comercial intermitente que rompen las botellas de marca.</p>

<h3>Por qué este dispensador jabón pared es distinto</h3>
<ul>
  <li>Capacidad de 500 ml: dura semanas sin recarga en uso doméstico.</li>
  <li>Diseño ergonómico, fácil de pulsar incluso con las manos enjabonadas.</li>
  <li>Material plástico resistente a la humedad del baño y a productos de limpieza suaves.</li>
  <li>Recargable con cualquier jabón líquido a granel (más económico que botellas).</li>
  <li>Instalación al muro con fijaciones incluidas.</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>El ROI silencioso de un dispensador jabón pared</h3>
<p>Comprar jabón a granel y recargar este dispensador cuesta entre 30% y 50% menos que comprar botellas individuales. En un baño de hogar familiar, el ahorro anual paga el dispensador en pocos meses. En oficinas o locales comerciales, el ahorro es aún más significativo. Y además del ahorro, ganas en estética y orden.</p>
<p>Si vas a renovar el equipamiento del baño, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Para qué espacios es ideal</h3>
<p>Baños de hogar (especialmente baños de visitas), oficinas, locales comerciales, restaurantes, cafés, colegios. Cualquier baño donde la imagen profesional importa y donde se aprecia el orden visual.</p>
<p>Para complementar, mira también nuestra <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a>.</p>

<h3>Despacho a todo Chile y respaldo Victtorino</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en accesorios y dispensadores. Despacho a todo Chile.</p>
<p><strong>Un dispensador jabón pared bien elegido eleva la estética y baja la cuenta de jabón al mismo tiempo.</strong></p>""",
}

PROD_2607 = {  # #20 — Agarradera 135° con Jabonera (27 ventas)
    "action": "PUT", "woo_id": 2607,
    "focus": "agarradera baño con jabonera",
    "meta_title": "Agarradera Baño 135° con Jabonera Acero Inox | Victtorino",
    "meta_desc": "Agarradera baño con jabonera integrada, ángulo 135° acero inoxidable plateado. Seguridad y funcionalidad en una sola pieza. Despacho a todo Chile.",
    "short_desc": "<p>La <strong>agarradera baño con jabonera</strong> integrada en ángulo 135°. Seguridad y funcionalidad combinadas, acero inoxidable durable. Despacho a todo Chile.</p>",
    "description": """<h2>Una agarradera baño con jabonera que combina seguridad y funcionalidad</h2>
<p>La <strong>agarradera baño con jabonera</strong> es esa solución elegante que combina dos cosas que normalmente requieren dos accesorios separados: la seguridad de una barra de agarre firme y la utilidad de tener un lugar fijo para el jabón. Ángulo 135° pensado para que el agarre sea natural mientras te apoyas para alcanzar el jabón, sin movimientos forzados.</p>
<p>Acero inoxidable de calidad, anclajes seguros incluidos, diseño contemporáneo que se integra al baño moderno sin esa estética hospitalaria que tienen muchas agarraderas convencionales.</p>

<h3>Por qué esta agarradera baño con jabonera es distinta</h3>
<ul>
  <li>Función doble: seguridad de agarre + ubicación fija para el jabón.</li>
  <li>Ángulo de 135°: ergonómico para alcanzar el jabón mientras te apoyas.</li>
  <li>Acero inoxidable resistente a la humedad permanente y al vapor de la ducha.</li>
  <li>Anclajes seguros para muros sólidos, tornillos y tarugos incluidos.</li>
  <li>Diseño moderno que se integra a baños contemporáneos sin gritar "hospital".</li>
  <li>Despacho a todo Chile con respaldo Victtorino.</li>
</ul>

<h3>Para quién es esta agarradera baño con jabonera</h3>
<p>Para hogares con abuelos donde la seguridad de la ducha es prioridad. Para baños de pacientes en recuperación. Para padres que quieren prevenir resbalones de sus hijos. Para adultos que un día se resbalaron en su propia ducha y entendieron que no es solo cosa de la tercera edad. Y para quienes simplemente valoran tener el jabón siempre en su lugar sin que se caiga al piso.</p>
<p>Si vas a equipar la ducha con seguridad completa, mira nuestra selección de <a href="https://victtorino.cl/categoria-producto/agarraderas-y-barras-para-bano/">agarraderas y barras de seguridad</a> y <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>

<h3>Instalación y compatibilidad</h3>
<p>Se instala sobre muro de albañilería o tabique reforzado. Para muros débiles recomendamos usar fijaciones químicas. Para complementar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>

<h3>Tranquilidad en cada ducha, hecha en serio</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en accesorios y seguridad de baño. Despacho a todo Chile.</p>
<p><strong>Una agarradera baño con jabonera es una de esas decisiones silenciosas que cuidan a tu familia todos los días.</strong></p>""",
}


PRODUCTOS = [PROD_3009, PROD_2578, PROD_NEW_LAVAPLATOS_100_DER, PROD_3117,
             PROD_2739, PROD_2783, PROD_3084, PROD_2607]


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
        "description": prod["description"],
        "short_description": prod["short_desc"],
        "meta_data": [
            {"key": "rank_math_title", "value": prod["meta_title"]},
            {"key": "rank_math_description", "value": prod["meta_desc"]},
            {"key": "rank_math_focus_keyword", "value": prod["focus"]},
        ],
    }
    return woo_request("PUT", f"/products/{prod['woo_id']}", json=body)


def aplicar_post(prod):
    cats = woo_request("GET", "/products/categories", params={"per_page": 100})
    cat_id_por_nombre = {c["name"]: c["id"] for c in cats}
    item = requests.get(f"https://api.mercadolibre.com/items/{prod['ml_id']}",
                        headers=ML_HEAD, timeout=30).json()
    titulo = item.get("title", "")
    precio = item.get("price")
    stock = int(item.get("available_quantity") or 0)
    pictures = [p["url"] for p in item.get("pictures", []) if p.get("url")]
    images_payload = [{"src": u, "alt": (titulo if i == 0 else f"{titulo} - foto {i+1}")[:120]}
                      for i, u in enumerate(pictures)]
    sku = f"ML-{prod['ml_id']}"
    existente = woo_request("GET", "/products", params={"sku": sku})
    if existente:
        print(f"  YA EXISTE Woo {existente[0]['id']}, hago PUT")
        prod["woo_id"] = existente[0]["id"]
        return aplicar_put(prod)
    body = {
        "name": titulo, "slug": slugify(titulo), "type": "simple", "status": "draft",
        "regular_price": str(int(precio)) if precio else "",
        "manage_stock": True, "stock_quantity": stock,
        "description": prod["description"], "short_description": prod["short_desc"],
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


print(f"Lote 2 — SEO premium INDIVIDUAL para {len(PRODUCTOS)} productos\n")
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
        links = res.get("description", "").count('href="')
        print(f"     OK Woo {res['id']} status={res.get('status')} palabras={pal} fk_count={fk_count} links={links}")
        resultados.append({"id": res["id"], "ok": True, "pal": pal, "fk_count": fk_count,
                           "focus": prod["focus"], "name": res.get("name", "")[:50]})
    else:
        print(f"     FALLO")
        resultados.append({"id": ident, "ok": False})
    time.sleep(2)

print("\n" + "=" * 70)
print(f"RESUMEN Lote 2: {sum(1 for r in resultados if r.get('ok'))}/{len(PRODUCTOS)}")
print("=" * 70)
for r in resultados:
    if r.get("ok"):
        print(f"  {r['id']:5} {r['pal']:4}pal fk{r['fk_count']:2}x \"{r['focus']:30}\" {r['name']}")

with open(r"C:\Users\dell\victtorino\seo_lote2_resultado.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
