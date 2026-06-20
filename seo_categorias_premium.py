"""
SEO premium para las 10 paginas de categoria principales de victtorino.cl.

Cada categoria recibe una description HTML expandida (~400-500 palabras) con:
- H2 con focus keyword principal de la categoria
- 3-4 H3 con focus en al menos 1
- Bullets de "que encontraras" y "como elegir"
- Enlaces internos a categorias relacionadas + externo a /nosotros/
- Tono inspiracional-hogar (mismo que aplicamos a productos)
"""
import json
import sys
import io
import time
import re
import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}


# ============================================================
# 10 CATEGORÍAS — descripciones premium
# ============================================================

CATS = {
    113: {  # Griferia
        "name": "Griferia",
        "focus": "grifería para baño",
        "description": """<h2>Grifería para baño que se nota desde el primer uso</h2>
<p>La <strong>grifería para baño</strong> es probablemente el elemento que más impacto visual tiene en una renovación de baño con menor inversión y menos obras. Una llave nueva, bien elegida, transforma la percepción del espacio completo: el lavamanos se ve cuidado, el shower se siente moderno, el día comienza distinto. En Victtorino reunimos la grifería para baño que aguanta el uso real del hogar chileno — agua dura, sales, productos de limpieza variados — sin perder su acabado en el primer año.</p>

<h3>Qué encontrarás en grifería</h3>
<ul>
  <li>Llaves monomando para lavatorio y lavaplatos en cromado, negro Schwartz y cepillado.</li>
  <li>Mezcladoras de baño y ducha con mecanismo cerámico de larga duración.</li>
  <li>Llaves temporizadas para baños institucionales y públicos con ahorro automático.</li>
  <li>Brazos, columnas y duchas fijas al muro para renovar el shower sin obras.</li>
  <li>Accesorios complementarios: flexibles, conexiones, llaves doble salida.</li>
</ul>

<h3>Cómo elegir la grifería para baño correcta</h3>
<p>Lo primero es decidir el acabado: el cromado clásico combina con todo pero muestra las manchas de agua dura; el negro Schwartz tiene presencia y disimula las huellas; el cepillado plateado es el favorito en baños contemporáneos. Después viene el tipo: monomando para máxima ergonomía y menor consumo, doble manilla para estilos más clásicos. Por último, el mecanismo interno: las cerámicas duran años más que las gomas tradicionales.</p>

<h3>Calidad pensada para hogares chilenos</h3>
<p>Cada pieza de grifería para baño que ofrecemos pasa por el filtro de uso real chileno: agua con presión variable, sales que dejan marca, productos de limpieza distintos en cada casa. Lo que dura en un catálogo idealizado no es lo mismo que dura en una casa con familia, varios baños al día y ritmo intenso. Por eso seleccionamos solo modelos que aguantan ese contexto.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena especializada en grifería y accesorios para baño. Para complementar tu renovación, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a> y <a href="https://victtorino.cl/categoria-producto/lavamanos/">lavamanos</a>.</p>""",
    },

    115: {  # Lavaplatos
        "name": "Lavaplatos",
        "focus": "lavaplatos de cocina",
        "description": """<h2>Lavaplatos de cocina que aguantan el ritmo de una casa chilena</h2>
<p>El <strong>lavaplatos de cocina</strong> es probablemente la pieza más usada de toda la casa: lavados diarios, ollas grandes, sartenes pesadas, cuchillos, restos de comida, agua caliente, productos de limpieza variados. Renovar el lavaplatos de cocina es una de las decisiones de mayor impacto en una cocina existente, y vale la pena hacerla bien — un buen lavaplatos dura 10+ años, uno barato toca cambiar en 3.</p>

<h3>Qué encontrarás en lavaplatos</h3>
<ul>
  <li>Lavaplatos empotrados 80x44 (la medida más común en cocinas chilenas).</li>
  <li>Lavaplatos 100x44 para cocinas familiares activas que necesitan más espacio.</li>
  <li>Opciones con secador izquierdo y derecho según dónde está tu llave.</li>
  <li>Modelos en acero inoxidable pulido de espesor durable.</li>
  <li>Packs completos con grifería, sifón y canastillo incluidos.</li>
</ul>

<h3>Cómo elegir el lavaplatos de cocina correcto</h3>
<p>Primero las dimensiones: 80x44 es el estándar y entra en muebles modulares chilenos sin adaptación. Si tu cocina tiene espacio para 100x44, gana 20 cm de cubeta y la diferencia en el día a día es notable. Segundo, el secador: el lado opuesto a tu grifería (si la llave está a la izquierda, secador derecho). Tercero, el espesor del acero — los lavaplatos delgados se abollan con el primer golpe de olla.</p>

<h3>Calidad para cocinas reales</h3>
<p>Cada lavaplatos de cocina del catálogo está elegido para aguantar familias grandes, ollas industriales y ritmo diario intenso. Acero inoxidable de calidad, geometría que escurre bien, terminación pulida que no se opaca con los meses. Lo que importa en un lavaplatos no es cómo se ve el primer día — es cómo se ve después de un año de uso real.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para completar la renovación de tu cocina, mira también nuestra <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para cocina</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>""",
    },

    117: {  # Lavamanos
        "name": "Lavamanos",
        "focus": "lavamanos para baño",
        "description": """<h2>Lavamanos para baño que se transforma en pieza decorativa</h2>
<p>El <strong>lavamanos para baño</strong> dejó hace tiempo de ser solo un sanitario funcional. Hoy es uno de los puntos visuales más importantes del baño: lo ves cuando entras, lo ves cuando sales, lo usas varias veces al día. Renovar el lavamanos para baño es una de las intervenciones de mayor impacto visual con menos obra — cambias el centro decorativo sin tocar pisos, paredes ni el WC.</p>

<h3>Qué encontrarás en lavamanos</h3>
<ul>
  <li>Lavamanos sobrepuestos de vidrio templado para baños contemporáneos.</li>
  <li>Modelos redondos, cuadrados y rectangulares según el estilo del baño.</li>
  <li>Acabados en cristal transparente, cerámica blanca y materiales nobles.</li>
  <li>Dimensiones compatibles con muebles y consolas estándar chilenos.</li>
  <li>Modelos para departamento, casa familiar y baños comerciales.</li>
</ul>

<h3>Cómo elegir el lavamanos para baño correcto</h3>
<p>Primero el tipo de instalación: sobrepuesto (descansa sobre el mesón, máximo impacto visual), empotrado (queda al ras, look más limpio), o de pedestal (clásico). Segundo, el tamaño — un lavamanos demasiado grande satura el baño chico, uno demasiado pequeño se pierde en un baño amplio. Tercero, el material — el vidrio templado se ve increíble pero requiere limpieza más cuidadosa; la cerámica clásica es a prueba de todo.</p>

<h3>Diseño que se mantiene en el tiempo</h3>
<p>Cada lavamanos para baño del catálogo está elegido por durabilidad real y diseño que no envejece en 6 meses. Los baños se renuevan cada 10-15 años en promedio — vale la pena elegir piezas que se vean bien todo ese tiempo, no solo el día que las compras.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para completar el conjunto del baño, mira también nuestra <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a>, <a href="https://victtorino.cl/categoria-producto/espejos/">espejos para baño</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios</a>.</p>""",
    },

    116: {  # Espejos
        "name": "Espejos",
        "focus": "espejos para baño",
        "description": """<h2>Espejos para baño que amplían el espacio y elevan la luz</h2>
<p>Los <strong>espejos para baño</strong> son mucho más que un reflejo: amplían visualmente espacios pequeños, mejoran la iluminación natural, y son el punto focal del baño moderno. Un espejo para baño bien elegido — del tamaño correcto, con iluminación si corresponde, con borde acorde al estilo — puede transformar la percepción de un baño completo sin tocar ninguna otra cosa.</p>

<h3>Qué encontrarás en espejos</h3>
<ul>
  <li>Espejos rectangulares modernos con luces LED integradas (fría, cálida o ambas).</li>
  <li>Espejos redondos con borde metálico para baños contemporáneos.</li>
  <li>Espejos con aumento (x3, x5) ideales para maquillaje y afeitado.</li>
  <li>Espejos de pedestal y de muro, según el espacio disponible.</li>
  <li>Modelos en distintos tamaños desde compactos hasta espejos amplios.</li>
</ul>

<h3>Cómo elegir los espejos para baño correctos</h3>
<p>Primero el tamaño: la regla simple es que el espejo no debe ser más ancho que el lavamanos, pero sí lo suficientemente alto para que la persona más alta de la casa se vea cómoda. Segundo, decide si quieres iluminación LED — cambia toda la dinámica del baño, especialmente en baños sin ventana. Tercero, considera el borde: marco oscuro define más, sin marco se ve más amplio, con luz LED queda flotante.</p>

<h3>Detalles que importan en baños chilenos</h3>
<p>La humedad permanente del baño (vapor de ducha, ventilación a veces limitada) puede picar el azogue de espejos baratos en pocos meses. Los espejos para baño del catálogo Victtorino tienen bordes sellados y soportes resistentes a la humedad — siguen viéndose como nuevos después de años de uso intensivo.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para completar tu baño, mira también <a href="https://victtorino.cl/categoria-producto/lavamanos/">lavamanos</a> y <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>.</p>""",
    },

    118: {  # Shower/Mamparas/Receptaculos
        "name": "Shower/Mamparas/Receptaculos",
        "focus": "mamparas y receptáculos de ducha",
        "description": """<h2>Mamparas y receptáculos de ducha que redefinen el baño</h2>
<p>Las <strong>mamparas y receptáculos de ducha</strong> transforman el área húmeda del baño como ninguna otra intervención. Una ducha bien delimitada se siente más amplia, más limpia, más privada y, sobre todo, más cómoda de usar todos los días. El resto del baño se mantiene seco, el vapor se contiene en la ducha, las toallas no quedan húmedas. Detalles que parecen menores hasta que los tienes — y entonces ya no quieres volver atrás.</p>

<h3>Qué encontrarás en mamparas y receptáculos</h3>
<ul>
  <li>Shower doors rectos y curvos en vidrio templado de seguridad.</li>
  <li>Receptáculos antideslizantes cuadrados y esquineros en distintas medidas.</li>
  <li>Platos de ducha con superficie texturizada para mayor seguridad.</li>
  <li>Brazos, columnas y duchas fijas al muro para el conjunto completo.</li>
  <li>Medidas estándar (80x80, 90x90) y opciones para baños más amplios.</li>
</ul>

<h3>Cómo elegir las mamparas y receptáculos correctos</h3>
<p>Primero las dimensiones — mide el espacio disponible en la esquina del baño y compara con las medidas estándar. Segundo, decide si quieres shower door curvo (aprovecha mejor la esquina) o recto (look más arquitectónico). Tercero, considera el receptáculo: antideslizante es no negociable si hay niños, abuelos o cualquiera que se duche con prisa. Cuarto, el vidrio templado es indispensable por seguridad.</p>

<h3>Pensado para baños chilenos reales</h3>
<p>El uso real de una ducha en una casa chilena pone a prueba cualquier mampara: vapor diario, agua caliente, productos de limpieza, baños familiares con frecuencia alta. Cada pieza de nuestras mamparas y receptáculos de ducha está elegida para resistir ese contexto durante años, no temporadas.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para complementar tu ducha, mira también nuestra <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a>, <a href="https://victtorino.cl/categoria-producto/agarraderas-y-barras-para-bano/">agarraderas y barras de seguridad</a> y <a href="https://victtorino.cl/categoria-producto/sifones-y-desagues/">sifones y desagües</a>.</p>""",
    },

    112: {  # Accesorios
        "name": "Accesorios",
        "focus": "accesorios para baño",
        "description": """<h2>Accesorios para baño que renuevan sin remodelar</h2>
<p>Los <strong>accesorios para baño</strong> son la forma más rápida, económica y de mayor impacto visual para renovar un baño sin meterse en una remodelación. Cambiar los accesorios un sábado en la mañana puede transformar la sensación del espacio completo sin tocar pisos, paredes ni sanitarios. Pequeños detalles que se ven todos los días, que se sienten cada vez que entras al baño, y que terminan ordenando visualmente todo el espacio.</p>

<h3>Qué encontrarás en accesorios</h3>
<ul>
  <li>Sets completos de accesorios con todas las piezas combinadas estéticamente.</li>
  <li>Toalleros, portarrollos, jaboneras y ganchos en distintos acabados.</li>
  <li>Basureros con pedal en acero inoxidable para higiene sin contacto.</li>
  <li>Brazos de ducha, organizadores esquineros y repisas funcionales.</li>
  <li>Flexibles, conexiones y piezas de instalación complementarias.</li>
</ul>

<h3>Cómo elegir accesorios para baño que combinen</h3>
<p>El secreto de un baño bien armado no es comprar cosas caras: es comprar cosas que conversen entre sí. Mismo acabado (plateado, cromado, negro Schwartz, cobre), mismo lenguaje de diseño (moderno minimalista, clásico renovado, industrial). Por eso recomendamos elegir los accesorios para baño por línea o por colección — toallero, portarrollos y jabonera de la misma familia se ven 10 veces mejor que tres piezas sueltas, aunque cada una sea individualmente bonita.</p>

<h3>Materiales que aguantan</h3>
<p>La humedad permanente del baño es exigente. Los accesorios para baño plásticos baratos se decoloran en meses; los metálicos baratos se oxidan en el primer año. En Victtorino seleccionamos solo accesorios con materiales que aguantan el uso real chileno: acero inoxidable de calidad, ABS reforzado, cromados resistentes al vapor.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para completar tu renovación, mira también <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a>, <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a> y <a href="https://victtorino.cl/categoria-producto/espejos/">espejos para baño</a>.</p>""",
    },

    114: {  # Dispensador
        "name": "Dispensador",
        "focus": "dispensador de jabón y papel",
        "description": """<h2>Dispensador de jabón y papel: higiene moderna en cada baño</h2>
<p>Un buen <strong>dispensador de jabón y papel</strong> es de esos detalles que separan un baño cuidado de uno descuidado. Si has visto baños de hoteles boutique, oficinas modernas o restaurantes bien diseñados, sabes que ninguno tiene botellas comerciales sobre el lavamanos o rollos de papel apoyados en cualquier lado. Tienen dispensadores discretos en la pared, integrados a la estética, recargables, ordenados. La diferencia entre un baño común y un baño profesional muchas veces está justo ahí.</p>

<h3>Qué encontrarás en dispensador</h3>
<ul>
  <li>Dispensadores de jabón líquido y alcohol gel en acero inoxidable.</li>
  <li>Dispensadores de papel higiénico para rollo industrial (mayor autonomía).</li>
  <li>Dispensadores de papel toalla interfoliada para baños públicos.</li>
  <li>Modelos manuales y automáticos con sensor sin contacto.</li>
  <li>Capacidades desde 300 ml hasta 1 litro según el uso esperado.</li>
</ul>

<h3>Cómo elegir el dispensador correcto</h3>
<p>Para baños de hogar, un dispensador de jabón y papel de 500 ml en acero inoxidable o ABS blanco entrega elegancia y autonomía suficiente. Para baños públicos comerciales, conviene ir a dispensadores de mayor capacidad — rollo industrial en papel higiénico, 1 litro en jabón — para reducir frecuencia de recargas. Si la imagen profesional es prioritaria, los modelos con sensor sin contacto elevan toda la experiencia.</p>

<h3>El ahorro silencioso de un buen dispensador</h3>
<p>Recargar dispensadores con jabón a granel cuesta entre 30% y 50% menos que comprar botellas individuales. En un hogar familiar el ahorro paga el dispensador en pocos meses; en oficinas o locales comerciales el ROI es aún más rápido. Y además del ahorro, ganas estética y orden visual permanente.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para complementar tu baño profesional o de hogar, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a> y <a href="https://victtorino.cl/categoria-producto/wc-e-inodoros/">WC e inodoros</a>.</p>""",
    },

    143: {  # Agarraderas y Barras
        "name": "Agarraderas y Barras",
        "focus": "agarraderas y barras de seguridad",
        "description": """<h2>Agarraderas y barras de seguridad: tranquilidad en cada ducha</h2>
<p>Las <strong>agarraderas y barras de seguridad</strong> son ese gesto silencioso que convierte un baño común en un espacio seguro y pensado para toda la familia. Para abuelos que viven con la familia, para niños que empiezan a ducharse solos, para personas con movilidad reducida, o simplemente para añadir ese punto extra de tranquilidad a la ducha diaria. Una agarradera bien instalada es invisible cuando no la necesitas y crucial cuando sí.</p>

<h3>Qué encontrarás en agarraderas y barras</h3>
<ul>
  <li>Barras rectas de 30, 40, 60 y 90 cm para ducha y zona de WC.</li>
  <li>Agarraderas en ángulo (90°, 135°) que aprovechan esquinas.</li>
  <li>Barras esquineras de 3 apoyos para máxima seguridad.</li>
  <li>Modelos con jabonera integrada que combinan dos funciones en una.</li>
  <li>Acabados en acero inoxidable pulido y negro contemporáneo.</li>
</ul>

<h3>Cómo elegir las agarraderas y barras correctas</h3>
<p>Primero ubica los puntos críticos: entrada de la ducha, junto al WC, donde hay cambio de nivel o resbalón potencial. Segundo, mide los espacios disponibles y elige el largo correcto (30 cm para apoyo puntual, 60+ cm para sostén firme al pararse). Tercero, prefiere acero inoxidable sobre otros materiales — aguanta humedad permanente sin oxidarse. Cuarto, asegúrate de instalar sobre muros sólidos con tornillos y tarugos firmes.</p>

<h3>Diseño que no grita "hospital"</h3>
<p>La seguridad no tiene que verse fea. Las agarraderas y barras de seguridad modernas tienen diseños limpios que se integran a baños contemporáneos sin esa estética hospitalaria que tenían los modelos antiguos. Acabados pulidos, formas curvas suaves, materiales nobles — seguridad con estilo.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para complementar la seguridad del baño completo, mira también nuestras <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a> y <a href="https://victtorino.cl/categoria-producto/wc-e-inodoros/">WC e inodoros</a>.</p>""",
    },

    144: {  # Sifones y Desagües
        "name": "Sifones y Desagües",
        "focus": "sifones y desagües",
        "description": """<h2>Sifones y desagües: lo que no se ve pero hace toda la diferencia</h2>
<p>Los <strong>sifones y desagües</strong> son de esos elementos que nadie celebra cuando funcionan bien, pero que se vuelven protagonistas cuando fallan: malos olores subiendo del alcantarillado, filtraciones bajo el mueble, agua que se acumula y tarda en bajar, atascos recurrentes. Cuando un sifón funciona, simplemente no piensas en él. Cuando funciona mal, condiciona toda la experiencia del baño o la cocina.</p>

<h3>Qué encontrarás en sifones y desagües</h3>
<ul>
  <li>Sifones de desagüe para lavamanos, lavaplatos y receptáculos de ducha.</li>
  <li>Desagües de lavaplatos 3 1/2 (114 mm) con sistema de rebalse.</li>
  <li>Sifones plásticos y metálicos en distintos diámetros (1 1/4, 1 1/2).</li>
  <li>Accesorios complementarios: codos, conexiones, rejillas, empaques.</li>
  <li>Modelos para tinas, receptáculos y desagües especiales.</li>
</ul>

<h3>Cómo elegir los sifones y desagües correctos</h3>
<p>Primero el diámetro: 1 1/4 para lavamanos, 1 1/2 para lavaplatos chicos, 3 1/2 (114 mm) para lavaplatos modernos y receptáculos. Segundo, el material: plástico es más económico y duradero contra corrosión química; metálico es más sólido contra golpes. Tercero, el tipo: con o sin rebalse (recomendado), con o sin reja-filtro (recomendado para cocina). Y cuarto, el sello hermético contra malos olores es no negociable.</p>

<h3>El ROI de un sifón bien elegido</h3>
<p>Un sifón barato puede fallar en 6-12 meses y arrastrar consigo daños mayores: muebles húmedos, pisos manchados, malos olores que llegan a invadir el baño completo. Un sifón de calidad cuesta poco más y dura años. Es una de las reparaciones de menor costo y mayor impacto preventivo que puedes hacer en la casa.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para completar la instalación, mira también nuestros <a href="https://victtorino.cl/categoria-producto/lavaplatos/">lavaplatos</a>, <a href="https://victtorino.cl/categoria-producto/lavamanos/">lavamanos</a> y <a href="https://victtorino.cl/categoria-producto/shower-mamparas-receptaculos/">mamparas y receptáculos de ducha</a>.</p>""",
    },

    145: {  # WC e Inodoros
        "name": "WC e Inodoros",
        "focus": "WC e inodoros",
        "description": """<h2>WC e inodoros: detalles para la pieza más usada del baño</h2>
<p>Los componentes para <strong>WC e inodoros</strong> son ese conjunto de piezas pequeñas que condicionan toda la experiencia del baño. Una válvula que cierra bien al primer intento, una tapa que no se afloja con el uso, un mecanismo que dura años sin fallar, un kit de estanque completo cuando llega el momento de renovar. Pequeñas diferencias que se acumulan en miles de usos al año.</p>

<h3>Qué encontrarás en WC e inodoros</h3>
<ul>
  <li>Kits completos para estanque WC con válvula carga, descarga y fijaciones.</li>
  <li>Válvulas laterales y de pie para mecanismos internos.</li>
  <li>Fluxómetros y válvulas de descarga para WC institucionales.</li>
  <li>Tapas de WC en distintos modelos y materiales.</li>
  <li>Componentes electrónicos para urinarios con sensor sin contacto.</li>
</ul>

<h3>Cómo elegir componentes para WC e inodoros</h3>
<p>Primero diagnóstica el problema: si el estanque se llena y nunca para, necesitas válvula de carga; si el agua se cuela hacia la taza, válvula de descarga; si ambas tienen tiempo, kit completo. Segundo, verifica el modelo de tu WC — la mayoría son monobloque estándar y aceptan kits universales, pero algunos modelos antiguos requieren piezas específicas. Tercero, prefiere materiales durables que aguanten la cloración del agua potable chilena.</p>

<h3>Para hogar y para baño institucional</h3>
<p>Los WC e inodoros en hogares chilenos resisten décadas, pero los componentes internos (válvulas, mecanismos, tapas) se desgastan y se reemplazan periódicamente. Renovar componentes es 90% más económico que cambiar el WC entero, y la diferencia en funcionamiento se nota desde el primer día. Para baños institucionales con uso intensivo, las válvulas temporizadas y electrónicas con sensor son la solución profesional para ahorrar agua y mejorar higiene.</p>

<h3>Despacho a todo Chile</h3>
<p>Conoce más sobre <a href="https://victtorino.cl/nosotros/">nuestra historia</a> como marca chilena. Para complementar tu renovación, mira también nuestros <a href="https://victtorino.cl/categoria-producto/accesorios/">accesorios para baño</a>, <a href="https://victtorino.cl/categoria-producto/dispensador/">dispensadores</a> y <a href="https://victtorino.cl/categoria-producto/griferia/">grifería para baño</a>.</p>""",
    },
}


def aplicar(cat_id, data):
    body = {"description": data["description"]}
    for n in range(1, 4):
        try:
            r = requests.put(f"{WC}/wp-json/wc/v3/products/categories/{cat_id}",
                             json=body, params=P, timeout=120)
            if r.status_code == 503:
                time.sleep(8 * n)
                continue
            if r.status_code >= 400:
                print(f"  HTTP {r.status_code}: {r.text[:200]}")
                return None
            return r.json()
        except Exception as e:
            print(f"  RED {type(e).__name__}; retry")
            time.sleep(4 * n)
    return None


print(f"Aplicando SEO premium a {len(CATS)} categorias\n")
ok = []
for cat_id, data in CATS.items():
    print(f"({len(ok)+1}/{len(CATS)}) cat {cat_id} '{data['name']}' focus='{data['focus']}'")
    res = aplicar(cat_id, data)
    if res:
        plain = re.sub(r"<[^>]+>", " ", res.get("description", ""))
        pal = len(plain.split())
        fk = data["focus"].lower()
        fk_count = plain.lower().count(fk)
        links = res.get("description", "").count('href="')
        print(f"     OK palabras={pal} fk_count={fk_count} links={links}")
        ok.append({"id": cat_id, "name": data["name"], "focus": data["focus"],
                   "pal": pal, "fk_count": fk_count, "links": links})
    time.sleep(2)

print("\n" + "=" * 70)
print(f"RESUMEN: {len(ok)}/{len(CATS)} categorias actualizadas")
print("=" * 70)
for r in ok:
    print(f"  {r['id']:4} {r['name']:32} pal={r['pal']:3} fk={r['fk_count']:2}x links={r['links']}")

with open(r"C:\Users\dell\victtorino\seo_categorias_resultado.json", "w", encoding="utf-8") as f:
    json.dump(ok, f, ensure_ascii=False, indent=2)
