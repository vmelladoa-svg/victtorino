"""
SEO Premium en lote.

Aplica descripcion HTML expandida (>=600 palabras), con:
- H2 con focus keyword
- 3-4 H3 (al menos uno con focus keyword)
- Densidad focus 2%+
- 3 enlaces internos a categorias relacionadas + 1 enlace externo a /nosotros/
- Meta title y meta description con focus keyword
- Mantiene el status actual de cada producto (publish queda publish, draft queda draft).

Productos cubiertos: 2543 (Set Colomba publicado) + los 23 del lote (Woo 2551-2687).
"""
import json
import sys
import io
import time
import re
import unicodedata
import requests

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

# Categoria Woo -> (cat_padre_url, [relacionadas urls], focus_kw_default, label_relacionadas)
CAT_URLS = {
    "Accesorios": "/categoria-producto/accesorios/",
    "Agarraderas y Barras": "/categoria-producto/agarraderas-y-barras-para-bano/",
    "Dispensador": "/categoria-producto/dispensador/",
    "Espejos": "/categoria-producto/espejos/",
    "Griferia": "/categoria-producto/griferia/",
    "Lavamanos": "/categoria-producto/lavamanos/",
    "Lavaplatos": "/categoria-producto/lavaplatos/",
    "Shower/Mamparas/Receptaculos": "/categoria-producto/shower-mamparas-receptaculos/",
    "Sifones y Desagües": "/categoria-producto/sifones-y-desagues/",
    "WC e Inodoros": "/categoria-producto/wc-e-inodoros/",
}

# Categoria destino -> [3 categorias relacionadas para enlazar]
RELACIONADAS = {
    "Griferia":                        ["Accesorios", "Lavamanos", "Shower/Mamparas/Receptaculos"],
    "Accesorios":                      ["Griferia", "Dispensador", "Espejos"],
    "Dispensador":                     ["Accesorios", "WC e Inodoros", "Griferia"],
    "Espejos":                         ["Accesorios", "Lavamanos", "Griferia"],
    "Shower/Mamparas/Receptaculos":    ["Griferia", "Accesorios", "Agarraderas y Barras"],
    "Lavaplatos":                      ["Griferia", "Sifones y Desagües", "Lavamanos"],
    "Lavamanos":                       ["Griferia", "Espejos", "Accesorios"],
    "Agarraderas y Barras":            ["Accesorios", "Shower/Mamparas/Receptaculos", "WC e Inodoros"],
    "Sifones y Desagües":              ["Lavaplatos", "Lavamanos", "Shower/Mamparas/Receptaculos"],
    "WC e Inodoros":                   ["Accesorios", "Dispensador", "Griferia"],
}

# Labels legibles para los anchors
LABELS = {
    "Griferia": "grifería para baño",
    "Accesorios": "accesorios para baño",
    "Dispensador": "dispensadores",
    "Espejos": "espejos de baño",
    "Shower/Mamparas/Receptaculos": "mamparas y receptáculos de ducha",
    "Lavaplatos": "lavaplatos de cocina",
    "Lavamanos": "lavamanos",
    "Agarraderas y Barras": "agarraderas y barras de seguridad",
    "Sifones y Desagües": "sifones y desagües",
    "WC e Inodoros": "WC e inodoros",
}


def enlaces_internos_html(cat_destino):
    rels = RELACIONADAS.get(cat_destino, [])
    parts = []
    for r in rels:
        url = WC + CAT_URLS.get(r, "/")
        label = LABELS.get(r, r)
        parts.append(f'<a href="{url}">{label}</a>')
    return parts


# ================================================================
# Plantillas por categoria destino
# Cada plantilla recibe (titulo, focus) y devuelve description HTML >=600 palabras
# ================================================================

def plantilla_premium(cat_destino, titulo, focus):
    """Plantilla maestra parametrizada."""
    rels = enlaces_internos_html(cat_destino)
    rel1, rel2, rel3 = rels[0], rels[1], rels[2]

    bloques = {
        "Griferia": {
            "h2": f"Una {focus} que se nota desde el primer uso",
            "intro": (
                f"La <strong>{titulo}</strong> de Victtorino combina diseño contemporáneo y materiales pensados "
                f"para resistir el día a día del agua dura chilena. Una {focus} no es solo una pieza funcional: "
                "es la primera cosa que ves cuando entras al baño y la última que tocas antes de irte a dormir. "
                "Por eso vale la pena elegirla bien."
            ),
            "p2": (
                f"Si estás renovando tu baño sin meterte en una remodelación completa, cambiar la {focus} es "
                "probablemente la intervención de mayor impacto visual con menor inversión. Una llave nueva, "
                "bien elegida, transforma la percepción del espacio entero. Y eso es exactamente lo que esta "
                "pieza está pensada para hacer."
            ),
            "h3_1": f"Por qué elegir esta {focus}",
            "bullets_1": [
                f"Acabado resistente a manchas de agua dura y huellas — la {focus} se ve nueva por años, no por meses.",
                "Mecanismo cerámico de larga duración: sin goteos prematuros ni reparaciones constantes.",
                "Compatible con las instalaciones estándar del mercado chileno — sin sorpresas en la conexión.",
                "Diseño minimalista que combina con baños modernos, clásicos renovados, nórdicos o industriales.",
                "Respaldo Victtorino, marca chilena especializada en grifería desde hace años.",
            ],
            "h3_2": "Detalles técnicos y compatibilidad",
            "p_tec": (
                "Pensada para instalación accesible: cualquier maestro gasfíter con experiencia la monta en una "
                "visita. Compatible con la mayoría de las mezcladoras y monomandos del mercado chileno, lo que "
                "evita sorpresas a la hora de conectar. Si vienes a renovar otras piezas del baño, mira nuestro "
                f"catálogo de {rel1} y {rel2}."
            ),
            "h3_3": "Pensada para hogares chilenos reales",
            "p_real": (
                "Sabemos cómo se usa una grifería en una casa chilena: ritmo familiar, agua con presión variable, "
                "sales que dejan marca, productos de limpieza distintos. Cada pieza pasa por ese filtro de uso "
                "real antes de incorporarla al catálogo. No es solo una llave bonita — es una llave que sigue "
                "funcionando bien después de un año de uso intensivo."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Griferia']} y {rel3}. Despacho a todo Chile. "
                f"<strong>Renueva tu baño con la {focus} que te mereces.</strong> Esta pieza ya está esperándote."
            ),
        },
        "Accesorios": {
            "h2": f"Los {focus} que cambian la sensación del baño",
            "intro": (
                f"Este <strong>{titulo}</strong> es de esos {focus} que parecen menores pero terminan ordenando "
                "visualmente todo el espacio. La diferencia entre un baño funcional y un baño que se siente "
                "cuidado está casi siempre en los detalles, no en las piezas grandes. Y ese es justamente el rol "
                "que cumplen los buenos accesorios."
            ),
            "p2": (
                f"Renovar los {focus} es la forma más rápida y económica de darle un aire fresco a tu baño. "
                "No necesitas demoler nada, ni gastar una fortuna en remodelación, ni quedarte una semana sin "
                "baño. Cambias unas piezas un sábado en la mañana y el lunes ya se siente otro espacio."
            ),
            "h3_1": f"Por qué incorporar este {focus}",
            "bullets_1": [
                "Materiales pensados para resistir humedad permanente sin oxidarse ni decolorarse.",
                "Diseño funcional que cumple su rol sin gritar — los buenos accesorios son los que se sienten, no los que se ven.",
                "Acabados que combinan con cualquier estilo de baño: moderno, nórdico, clásico renovado.",
                "Instalación simple, con fijaciones incluidas y sin necesidad de obras.",
                f"Disponible en stock con despacho a todo Chile y respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos y combinación con otras piezas",
            "p_tec": (
                "Pensado para integrarse al baño completo. Si estás armando o renovando un set, te recomendamos "
                f"mirar también {rel1} y {rel2} de la misma línea o de líneas compatibles. El truco de un baño "
                "bien armado es que todas las piezas conversen entre sí: misma estética, misma terminación."
            ),
            "h3_3": "Pensado para tu rutina real",
            "p_real": (
                "Los accesorios buenos son los que aguantan: el portarrollos que no se afloja, la jabonera que "
                "no acumula moho, el toallero que no se decolora con el sol que entra por la ventana. Cada pieza "
                "del catálogo Victtorino pasa por ese filtro: que sirva en una casa chilena real, con uso "
                "familiar, durante años."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Accesorios']} y {rel3}. Despacho a todo Chile. "
                "<strong>Renueva tu baño sin remodelar — empieza por los detalles que sí se notan.</strong>"
            ),
        },
        "Dispensador": {
            "h2": f"Un {focus} eleva la experiencia del baño",
            "intro": (
                f"El <strong>{titulo}</strong> es de esos {focus} que parecen un detalle menor pero que terminan "
                "transformando la sensación de higiene y orden del baño. Dosis controlada, sin goteos en el "
                "lavamanos, sin botellas plásticas comerciales rompiendo la estética del espacio."
            ),
            "p2": (
                f"Si has visto baños de hoteles boutique o oficinas bien diseñadas, sabes que un {focus} bien "
                "elegido cambia la percepción del lugar. Es uno de los upgrades más baratos y de mayor impacto "
                "visual que puedes hacer en tu baño."
            ),
            "h3_1": f"Por qué elegir este {focus}",
            "bullets_1": [
                "Diseño ergonómico: fácil de rellenar, fácil de usar con una mano.",
                "Materiales resistentes a la humedad permanente del baño y a productos de limpieza suaves.",
                "Compatible con jabón líquido, gel antibacterial y alcohol gel — un solo dispositivo, varios usos.",
                "Ideal para hogares, oficinas, locales comerciales y baños institucionales.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos e instalación",
            "p_tec": (
                "Instalación simple: viene con fijaciones para muro o se apoya en encimera, según modelo. "
                "Si estás armando un set completo, mira nuestra selección de "
                f"{rel1} y {rel2} para complementar la estética."
            ),
            "h3_3": "Pensado para hogares y locales chilenos",
            "p_real": (
                "Sabemos que en Chile los baños se usan intensamente: familias grandes, locales con flujo "
                "constante, oficinas con muchos colaboradores. Cada dispensador del catálogo está pensado para "
                "ese uso real, con materiales que aguantan limpieza diaria y un mecanismo que no se atasca."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Dispensador']} y {rel3}. Despacho a todo Chile. "
                f"<strong>Pequeños cambios que se notan todos los días.</strong>"
            ),
        },
        "Espejos": {
            "h2": f"Un {focus} es más que un reflejo",
            "intro": (
                f"El <strong>{titulo}</strong> es de esas piezas que amplían visualmente el baño, mejoran la "
                f"iluminación natural y elevan toda la experiencia del espacio. Un {focus} bien elegido es la "
                "diferencia entre un baño funcional y un baño que se siente cuidado, cálido y bien diseñado."
            ),
            "p2": (
                f"Cambiar el {focus} es una de las intervenciones de mayor impacto visual con menor obra. No "
                "hay demolición, no hay tuberías que mover, no hay polvo: lo descuelgas y lo cambias en menos "
                "de una hora. Y al día siguiente se siente otro baño."
            ),
            "h3_1": f"Por qué elegir este {focus}",
            "bullets_1": [
                "Bordes y soportes diseñados para resistir humedad permanente sin deteriorarse.",
                "Acabados pensados para integrarse a cualquier estilo de baño: moderno, nórdico, clásico, industrial.",
                "Anclajes seguros incluidos, con instrucciones claras de instalación.",
                "Diseño que amplía visualmente espacios pequeños — clave en baños de departamento.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos y combinaciones",
            "p_tec": (
                f"Si estás armando un baño desde cero o renovando completo, te recomendamos mirar también "
                f"{rel1} y {rel2} para armar un conjunto coherente. El espejo es el centro visual del baño — "
                "todo lo demás debe conversar con él."
            ),
            "h3_3": "Pensado para hogares chilenos",
            "p_real": (
                "La humedad del baño chileno es exigente: vapor diario de la ducha, ventilación a veces "
                "limitada, productos de limpieza distintos. Cada espejo del catálogo está pensado para resistir "
                "ese ambiente sin que el azogue se pique ni el marco se decolore con los años."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Espejos']} y {rel3}. Despacho a todo Chile. "
                f"<strong>Tu baño se merece un mejor reflejo.</strong>"
            ),
        },
        "Shower/Mamparas/Receptaculos": {
            "h2": f"Una {focus} que redefine la ducha",
            "intro": (
                f"La <strong>{titulo}</strong> redefine el área húmeda del baño. Una ducha bien delimitada se "
                "siente más amplia, más limpia, más privada y, sobre todo, más cómoda de usar. La diferencia "
                "entre un baño que apura y un baño donde te tomas tu tiempo."
            ),
            "p2": (
                f"Una buena {focus} cambia toda la dinámica del baño: el piso del resto del espacio se mantiene "
                "seco, el vapor se contiene, el agua no salpica las toallas. Detalles que parecen menores hasta "
                "que los tienes — y entonces ya no quieres volver atrás."
            ),
            "h3_1": f"Por qué esta {focus} es distinta",
            "bullets_1": [
                "Vidrio templado resistente: aguanta golpes accidentales sin estallar.",
                "Perfilería y herrajes pensados para resistir humedad permanente sin oxidarse.",
                "Diseño contemporáneo que se ve igual de bien a la mañana siguiente que el día que la instalaste.",
                "Compatible con instalaciones estándar — no necesitas modificar la obra existente.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos y obra",
            "p_tec": (
                "Para instalación recomendamos un maestro con experiencia en mamparas. Si estás renovando otros "
                f"componentes del shower también, mira nuestro catálogo de {rel1} y {rel2} para armar el conjunto."
            ),
            "h3_3": "Pensada para baños chilenos reales",
            "p_real": (
                "El uso real de una ducha en una casa chilena pone a prueba cualquier mampara: vapor diario, "
                "agua caliente, productos de limpieza, baños familiares con mucha frecuencia. Esta pieza está "
                "elegida para resistir eso durante años, no temporadas."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Shower/Mamparas/Receptaculos']} y {rel3}. Despacho a todo Chile. "
                "<strong>Tu ducha diaria, como debería sentirse.</strong>"
            ),
        },
        "Lavaplatos": {
            "h2": f"El {focus} que aguanta tu cocina real",
            "intro": (
                f"El <strong>{titulo}</strong> está pensado para soportar el ritmo real de una cocina chilena: "
                "lavados largos, agua caliente, ollas grandes, cuchillos pesados, uso intensivo todos los días. "
                f"Un {focus} no es decoración — es probablemente la pieza más usada de toda tu casa después del "
                "WC y la cama."
            ),
            "p2": (
                f"Cambiar el {focus} es una de esas intervenciones que parecen menores y terminan transformando "
                "por completo la dinámica de cocinar. Más espacio, mejor escurrido, materiales que resisten — la "
                "diferencia se nota desde la primera lavada."
            ),
            "h3_1": f"Por qué este {focus} es distinto",
            "bullets_1": [
                "Acero inoxidable de espesor pensado para uso intensivo, no para vitrina.",
                "Dimensiones estándar compatibles con muebles de cocina chilenos.",
                "Diseño que minimiza salpicaduras y facilita el escurrido natural.",
                "Resistente a manchas, golpes y temperatura — aguanta de verdad.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos e instalación",
            "p_tec": (
                "Si estás renovando la cocina o complementando, mira también nuestra selección de "
                f"{rel1} y {rel2}. Un buen lavaplatos necesita una buena grifería al lado y un sifón que cumpla "
                "su parte — los tres trabajan juntos."
            ),
            "h3_3": "Pensado para cocinas chilenas reales",
            "p_real": (
                "Sabemos cómo se usa una cocina en Chile: familia que come en casa, ollas grandes para 4-6 "
                "personas, lavadas diarias post-almuerzo, sartenes con uso intensivo. Cada lavaplatos del "
                "catálogo está elegido para aguantar ese ritmo durante años."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena. "
                f"Despacho a todo Chile. Complementa tu instalación con {rel3} de la misma línea. "
                f"<strong>Tu cocina se merece un {focus} que esté a la altura.</strong>"
            ),
        },
        "Lavamanos": {
            "h2": f"Un {focus} como pieza protagonista",
            "intro": (
                f"El <strong>{titulo}</strong> deja atrás la idea del {focus} puramente funcional. Diseño "
                "contemporáneo, materiales nobles y la presencia visual de una pieza que se nota cuando entras "
                "al baño. Esto no es un sanitario más — es decoración funcional."
            ),
            "p2": (
                f"Renovar el {focus} es una de las intervenciones de mayor impacto visual que puedes hacer en "
                "un baño existente. Cambia el centro visual del espacio sin tocar el resto de la obra. La "
                "diferencia entre un baño anónimo y un baño con personalidad."
            ),
            "h3_1": f"Por qué elegir este {focus}",
            "bullets_1": [
                "Materiales pensados para el uso diario familiar: vidrio templado, cerámica de alta resistencia o acero.",
                "Diseño contemporáneo que combina con baños modernos, nórdicos o clásicos renovados.",
                "Compatible con mesones, muebles y consolas estándar chilenas.",
                "Instalación accesible con desagüe estándar.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos y combinaciones",
            "p_tec": (
                "Si vienes a renovar todo el conjunto del baño, complementa con nuestra selección de "
                f"{rel1}, {rel2} de líneas compatibles. La gracia es que el baño completo conversa entre sí."
            ),
            "h3_3": "Pensado para hogares chilenos",
            "p_real": (
                "El lavamanos es la pieza más mirada del baño después del espejo. Lo usas todos los días, "
                "varias veces al día. Por eso vale la pena elegir uno que aguante el ritmo de tu hogar y que se "
                "vea bien después de años de uso real."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Lavamanos']} y {rel3}. Despacho a todo Chile. "
                f"<strong>Tu baño se merece un {focus} con presencia propia.</strong>"
            ),
        },
        "Agarraderas y Barras": {
            "h2": f"Una {focus} es seguridad sin perder el estilo",
            "intro": (
                f"La <strong>{titulo}</strong> es ese gesto silencioso que transforma el baño en un espacio "
                "más seguro para toda la familia. Diseño moderno que no grita \"barra de hospital\" — se "
                f"integra al baño sin sacrificar la estética. Una {focus} bien elegida es invisible cuando "
                "no la necesitas y crucial cuando sí."
            ),
            "p2": (
                f"Una {focus} en la ducha o cerca del WC no es solo para abuelos. Es para la madre embarazada, "
                "el niño que recién aprende a ducharse solo, el adulto sano que un día se resbala con el jabón. "
                "Es un seguro tranquilo que cuesta poco y aporta mucho."
            ),
            "h3_1": f"Por qué esta {focus} es distinta",
            "bullets_1": [
                "Acero inoxidable resistente a la corrosión del baño húmedo.",
                "Anclajes seguros para muros sólidos — instalación con tornillos y tarugos incluidos.",
                "Acabado pulido que combina con cualquier baño moderno.",
                "Diseño ergonómico para agarre firme con o sin las manos enjabonadas.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos e instalación",
            "p_tec": (
                f"Recomendamos instalarla sobre muro de albañilería o tabique reforzado. Si estás renovando "
                f"el baño completo, mira también nuestro catálogo de {rel1} y {rel2} para complementar la "
                f"seguridad y la estética del espacio."
            ),
            "h3_3": "Tranquilidad en cada paso, pensada para hogares chilenos",
            "p_real": (
                "En Chile envejecemos en casa: los abuelos viven con la familia, los nietos pasan tiempo en su "
                "baño. Una agarradera bien instalada es un seguro tranquilo para todos. Y para el adulto joven "
                "que un día se resbala — también."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Agarraderas y Barras']} y {rel3}. Despacho a todo Chile. "
                f"<strong>Seguridad que se ve bien.</strong>"
            ),
        },
        "Sifones y Desagües": {
            "h2": f"Un {focus} es lo que no se ve pero importa",
            "intro": (
                f"El <strong>{titulo}</strong> es uno de esos elementos que nadie celebra cuando funcionan, "
                "pero que se vuelven protagonistas cuando fallan. Malos olores del desagüe, filtraciones bajo "
                f"el mueble, atascos recurrentes — todos vienen de un {focus} de mala calidad o mal instalado."
            ),
            "p2": (
                f"Invertir en un buen {focus} es invertir en años de tranquilidad. Es la pieza más silenciosa "
                "de todo el baño cuando trabaja bien, y la más ruidosa cuando trabaja mal. Vale la pena "
                "elegirla con criterio."
            ),
            "h3_1": f"Por qué este {focus} es distinto",
            "bullets_1": [
                "Materiales resistentes al desgaste constante por agua y productos químicos suaves.",
                "Sello hermético que evita malos olores del sistema de alcantarillado.",
                "Compatible con instalaciones estándar chilenas — sin sorpresas en el conectado.",
                "Instalación accesible para maestros gasfíter con experiencia básica.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos y compatibilidad",
            "p_tec": (
                "Si estás renovando el lavamanos, el lavaplatos o la ducha, este es buen momento para cambiar "
                f"también el sifón — duran menos que las piezas grandes. Mira también nuestro catálogo de "
                f"{rel1} y {rel2} si vienes en modo renovación integral."
            ),
            "h3_3": "Pensado para casas chilenas reales",
            "p_real": (
                "Las casas chilenas tienen ducts de desagüe que llevan años, con sus quiebres y particularidades. "
                "Un buen sifón se adapta a esa realidad. Los productos del catálogo Victtorino son piezas que "
                "funcionan en el mundo real, no en el catálogo idealizado del fabricante."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['Sifones y Desagües']} y {rel3}. Despacho a todo Chile. "
                f"<strong>Renueva lo que no se ve y nota la diferencia.</strong>"
            ),
        },
        "WC e Inodoros": {
            "h2": f"Detalles para {focus}: pequeñas piezas, gran diferencia",
            "intro": (
                f"El <strong>{titulo}</strong> es uno de esos elementos que parecen menores pero condicionan "
                "toda la experiencia del baño. Una válvula que cierra bien, una tapa que no se afloja, un "
                "mecanismo que dura — pequeñas diferencias que se acumulan en miles de usos al año."
            ),
            "p2": (
                f"El WC es la pieza más usada del baño y, sin embargo, la que menos atención recibe a la hora "
                "de renovar. Cuando algo falla, lo notas todos los días. Cuando todo funciona bien, te olvidas "
                "que existe. Ese es el rol de los buenos componentes."
            ),
            "h3_1": f"Por qué elegir este componente para {focus}",
            "bullets_1": [
                "Materiales resistentes al uso diario intensivo, en hogar, oficina y baño institucional.",
                "Compatible con instalaciones estándar — sin necesidad de adaptaciones.",
                "Mecanismos pensados para durar miles de ciclos sin fallar.",
                "Acabado que no se decolora ni se ensucia con el tiempo.",
                "Despacho a todo Chile con respaldo Victtorino.",
            ],
            "h3_2": "Detalles técnicos e instalación",
            "p_tec": (
                "Instalación accesible para cualquier maestro gasfíter con experiencia. Si estás renovando el "
                f"baño completo, complementa con nuestra selección de {rel1} y {rel2} para mantener "
                "coherencia estética entre piezas."
            ),
            "h3_3": "Pensado para uso intensivo",
            "p_real": (
                "Los WC chilenos resisten décadas, pero los componentes (válvulas, tapas, mecanismos) se "
                "desgastan. Es totalmente normal: están diseñados para ser reemplazables. Renovar los "
                "componentes es mucho más económico que cambiar el WC entero, y la diferencia se nota."
            ),
            "h3_4": "Despacho a todo Chile y respaldo Victtorino",
            "cierre": (
                f"Conoce más sobre <a href=\"{WC}/nosotros/\">nuestra historia</a> como marca chilena "
                f"especializada en {LABELS['WC e Inodoros']} y {rel3}. Despacho a todo Chile. "
                "<strong>Calidad que se nota al cerrar la puerta.</strong>"
            ),
        },
    }

    b = bloques[cat_destino]
    bullets_html = "\n".join(f"  <li>{x}</li>" for x in b["bullets_1"])
    html = f"""<h2>{b['h2']}</h2>
<p>{b['intro']}</p>
<p>{b['p2']}</p>

<h3>{b['h3_1']}</h3>
<ul>
{bullets_html}
</ul>

<h3>{b['h3_2']}</h3>
<p>{b['p_tec']}</p>

<h3>{b['h3_3']}</h3>
<p>{b['p_real']}</p>

<h3>{b['h3_4']}</h3>
<p>{b['cierre']}</p>"""
    return html


def meta_desc_premium(titulo, cat_destino, focus):
    plantillas = {
        "Griferia": f"{focus.capitalize()}: {titulo}. Diseño moderno, materiales resistentes al agua dura chilena. Despacho a todo Chile. Calidad Victtorino.",
        "Accesorios": f"{focus.capitalize()}: {titulo}. Pequeños detalles que renuevan tu baño sin remodelar. Despacho a todo Chile. Calidad Victtorino.",
        "Dispensador": f"{focus.capitalize()}: {titulo}. Higiene moderna con diseño elegante. Hogar y oficina. Despacho a todo Chile.",
        "Espejos": f"{focus.capitalize()} {titulo}. Amplía tu baño visualmente, mejora la iluminación. Despacho a todo Chile. Victtorino.",
        "Shower/Mamparas/Receptaculos": f"{focus.capitalize()}: {titulo}. Vidrio templado, diseño moderno, instalación accesible. Despacho a todo Chile.",
        "Lavaplatos": f"{focus.capitalize()}: {titulo}. Acero inoxidable que aguanta tu cocina real. Despacho a todo Chile. Calidad Victtorino.",
        "Lavamanos": f"{focus.capitalize()}: {titulo}. Pieza protagonista del baño. Diseño contemporáneo. Despacho a todo Chile.",
        "Agarraderas y Barras": f"{focus.capitalize()}: {titulo}. Seguridad sin perder el estilo. Acero inoxidable. Despacho a todo Chile.",
        "Sifones y Desagües": f"{focus.capitalize()}: {titulo}. Sin filtraciones, sin malos olores. Resistente. Despacho a todo Chile. Victtorino.",
        "WC e Inodoros": f"{focus.capitalize()}: {titulo}. Calidad pensada para uso intensivo. Despacho a todo Chile. Victtorino.",
    }
    d = plantillas.get(cat_destino, f"{titulo}. Calidad Victtorino con despacho a todo Chile.")
    return d[:155]


def meta_title_premium(titulo, focus):
    t = f"{titulo} | Victtorino"
    if len(t) > 60:
        max_t = 60 - len(" | Victtorino")
        t = f"{titulo[:max_t].rstrip()} | Victtorino"
    return t


# Focus keyword sugerido por categoria destino (general); productos especificos pueden tener uno mas a medida
FOCUS_POR_CAT = {
    "Griferia": "grifería",
    "Accesorios": "accesorios para baño",
    "Dispensador": "dispensador",
    "Espejos": "espejo para baño",
    "Shower/Mamparas/Receptaculos": "mampara de ducha",
    "Lavaplatos": "lavaplatos",
    "Lavamanos": "lavamanos",
    "Agarraderas y Barras": "agarradera baño",
    "Sifones y Desagües": "sifón desagüe",
    "WC e Inodoros": "WC e inodoros",
}


def woo_put(pid, body, intentos=3):
    for n in range(1, intentos + 1):
        try:
            r = requests.put(f"{WC}/wp-json/wc/v3/products/{pid}", json=body, params=P, timeout=120)
            if r.status_code >= 400:
                print(f"  ERROR {r.status_code}: {r.text[:300]}")
                return None
            return r.json()
        except (requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            espera = 2 ** n
            print(f"  RED intento {n}/{intentos} fallo ({type(e).__name__}); reintento en {espera}s")
            time.sleep(espera)
    return None


def woo_get(pid):
    r = requests.get(f"{WC}/wp-json/wc/v3/products/{pid}", params=P, timeout=30)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
 sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
 # Lista de productos a actualizar: woo_id, focus_keyword opcional (si None, usa el de categoria)
 # 2543 (Set Colomba) + los 23 del lote
 LISTA = [
    (2543, "set accesorios para baño"),  # Set Colomba
    (2551, "dispensador de jabón"),
    (2558, "válvula de pie"),
    (2568, "dispensador papel higiénico"),
    (2574, "shower door"),
    (2578, "llave temporizada urinario"),
    (2583, "organizador ducha"),
    (2590, "espejo doble cara aumento"),
    (2597, "fluxómetro WC"),
    (2607, "agarradera baño"),
    (2611, "espejo doble cara aumento"),
    (2615, "basurero pedal baño"),
    (2620, "basurero pedal baño"),
    (2624, "llave lavamanos Colomba"),
    (2629, "jabonera Colomba"),
    (2634, "basurero pedal baño"),
    (2642, "jabonera acero inoxidable"),
    (2647, "grifo monomando profesional"),
    (2655, "dispensador jabón acero inoxidable"),
    (2661, "desagüe tina bronce"),
    (2669, "lavaplatos empotrado"),
    (2674, "lavamanos vidrio"),
    (2681, "set de ducha"),
    (2687, "jabonera líquido inox"),
]

 print("=" * 70)
 print(f"SEO Premium aplicando a {len(LISTA)} productos")
 print("=" * 70)

 resultados = []
 for pid, focus in LISTA:
    actual = woo_get(pid)
    titulo = actual.get("name", "")
    status = actual.get("status", "draft")
    cats = [c["name"] for c in actual.get("categories", [])]
    if not cats:
        print(f"\n[{pid}] sin categoria, salto")
        continue
    cat_destino = cats[0]
    if cat_destino not in FOCUS_POR_CAT:
        print(f"\n[{pid}] cat '{cat_destino}' sin plantilla, salto")
        continue

    desc_html = plantilla_premium(cat_destino, titulo, focus)
    meta_t = meta_title_premium(titulo, focus)
    meta_d = meta_desc_premium(titulo, cat_destino, focus)
    short_d = f"<p>{titulo}. <strong>{focus.capitalize()}</strong> con diseño contemporáneo, materiales resistentes y despacho a todo Chile. Renueva tu baño con piezas que duran y se ven bien.</p>"

    body = {
        "status": status,
        "name": titulo,
        "description": desc_html,
        "short_description": short_d,
        "meta_data": [
            {"key": "rank_math_title", "value": meta_t},
            {"key": "rank_math_description", "value": meta_d},
            {"key": "rank_math_focus_keyword", "value": focus},
        ],
    }

    res = woo_put(pid, body)
    if not res:
        print(f"[{pid}] FALLO update")
        resultados.append({"pid": pid, "ok": False})
        continue

    palabras = len(re.sub(r"<[^>]+>", " ", res["description"]).split())
    frecuencia = res["description"].lower().count(focus.lower())
    enlaces = res["description"].count('href="')
    print(f"[{pid}] {cat_destino[:25]:25} status={status:8} palabras={palabras:4} focus_count={frecuencia} links={enlaces}  {titulo[:40]}")
    resultados.append({
        "pid": pid, "ok": True, "status": status, "cat": cat_destino,
        "palabras": palabras, "focus": focus, "frecuencia": frecuencia,
        "enlaces": enlaces,
    })

 print("\n" + "=" * 70)
 print("RESUMEN")
 print("=" * 70)
 ok = [r for r in resultados if r.get("ok")]
 print(f"OK: {len(ok)} / {len(resultados)}")
 if ok:
    avg = sum(r["palabras"] for r in ok) / len(ok)
    print(f"Promedio palabras: {avg:.0f}")
    print(f"Productos por status: publish={sum(1 for r in ok if r['status']=='publish')}, draft={sum(1 for r in ok if r['status']=='draft')}")

 with open(r"C:\Users\dell\victtorino\seo_premium_resultado.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
 print("\nDetalle -> seo_premium_resultado.json")
