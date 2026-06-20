"""Inyecta JSON-LD FAQPage schema al final de la descripción de cada categoría."""
import sys, io, json, time, requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WC = "https://victtorino.cl"
P = {"consumer_key": "ck_0c13f81e932be64b0a2c8ba340db4717ef6b5c15",
     "consumer_secret": "cs_3604e7ebdb8ff78442731344cc95af50516188a5"}

# Mismas 50 FAQs (5 por cat) que aplicamos en faq_categorias.py
FAQS = {
    113: [  # Grifería
        ("¿Qué tipo de grifería es mejor: monomando o doble manilla?",
         "Para baños y cocinas modernas el monomando es la opción favorita: controlas temperatura y caudal con una sola palanca, gastas menos agua mientras encuentras el punto correcto y la ergonomía es superior. La doble manilla queda mejor en baños clásicos o renovados con estética vintage."),
        ("¿Cuánto dura una llave de grifería de calidad?",
         "Una grifería con mecanismo cerámico de calidad dura entre 8 y 15 años en uso doméstico normal. Las llaves baratas con juntas de goma pueden comenzar a gotear al año o dos. Invertir en el mecanismo correcto evita reparaciones constantes."),
        ("¿La grifería negra o cromada es más duradera?",
         "Ambas duran lo mismo si son de calidad. El acabado negro Schwartz disimula mejor las manchas de agua dura chilena y huellas digitales, por eso requiere menos limpieza diaria. El cromado clásico se ve más brillante pero marca cada gota."),
        ("¿Es difícil cambiar la grifería?",
         "No. Cualquier maestro gasfíter con experiencia básica cambia una llave de lavamanos o ducha en 30-60 minutos. Lo único importante es cerrar la llave de paso antes y verificar que las conexiones son compatibles con las instalaciones estándar chilenas."),
        ("¿Cómo elijo la grifería para el lavaplatos?",
         "Considera tres cosas: altura (alta para ollas grandes, normal para uso estándar), tipo de pico (extensible si necesitas alcance, fijo si prefieres estabilidad) y acabado (cromado universal, negro o cepillado para diseño moderno)."),
    ],
    115: [  # Lavaplatos
        ("¿Qué medida de lavaplatos es la más común en Chile?",
         "La medida 80x44 cm es el estándar más vendido en Chile porque entra perfecto en muebles modulares de cocina estándar. Para cocinas familiares activas, el 100x44 ofrece 20 cm extra de cubeta sin requerir mueble especial."),
        ("¿Cómo decido entre secador izquierdo o derecho?",
         "Depende de la ubicación de tu llave: si la grifería queda a la izquierda, elige secador derecho (para lavar a la izquierda y escurrir a la derecha sin chocar). Si la llave está a la derecha, elige secador izquierdo."),
        ("¿Es mejor un lavaplatos empotrado o sobrepuesto?",
         "El empotrado se ve más limpio y moderno (queda al ras del mesón), requiere corte preciso en el mueble. El sobrepuesto es más fácil de instalar (se apoya sobre el mesón), ideal para reemplazos rápidos sin obras de carpintería."),
        ("¿El acero inoxidable se mancha con el tiempo?",
         "El acero inoxidable de calidad no se mancha permanentemente. Pueden quedar marcas temporales de agua dura o cal que se quitan con un paño y vinagre diluido. Los lavaplatos baratos sí pueden picarse u oxidarse en zonas con golpes."),
        ("¿Qué incluye un pack de lavaplatos?",
         "Un pack completo incluye normalmente: lavaplatos, grifería monomando, sifón y canastillo (rejilla del desagüe). Ahorra entre 20-30% versus comprar las piezas por separado y garantiza que todas las medidas calzan."),
    ],
    117: [  # Lavamanos
        ("¿Qué tipo de lavamanos es mejor para baños pequeños?",
         "Para baños de departamento o ampliaciones, recomendamos lavamanos compactos (40-45 cm de ancho), redondos o cuadrados, instalación sobre mesón o consola flotante para liberar espacio visual en el piso."),
        ("¿Los lavamanos de vidrio son frágiles?",
         "No. Los lavamanos de vidrio templado de calidad resisten golpes accidentales, agua caliente y productos de limpieza estándar sin agrietarse. La templación los hace varias veces más resistentes que el vidrio común."),
        ("¿Necesito un lavamanos con rebalse?",
         "Los lavamanos con rebalse evitan desbordes si olvidas cerrar la llave. Para hogares con niños o uso intensivo, es muy recomendable. En baños de visita de uso esporádico no es crítico."),
        ("¿Qué mantención requiere un lavamanos?",
         "Limpieza con paño suave y productos no abrasivos. Evitar lejía concentrada y limpiadores con partículas. Una vez al mes revisar la silicona del borde para prevenir filtraciones."),
        ("¿Puedo cambiar el lavamanos sin tocar el mueble?",
         "Si el nuevo lavamanos tiene las mismas dimensiones de instalación y desagüe, sí. Los modelos estándar chilenos comparten medidas de fijación. Para cambios de tipo (empotrado a sobrepuesto), suele requerir adaptación del mueble."),
    ],
    116: [  # Espejos
        ("¿Los espejos LED para baño valen la pena?",
         "Sí, especialmente en baños sin ventana o con poca luz natural. La iluminación LED integrada mejora la visibilidad para afeitado y maquillaje, y reduce sombras duras. Modelos con luz fría-cálida intercambiable cubren ambos usos."),
        ("¿Qué tamaño de espejo debo elegir?",
         "Como regla, el espejo no debe ser más ancho que el lavamanos. La altura ideal cubre desde el pecho hasta la cabeza de la persona más alta de la casa. En baños chicos, espejos amplios amplían visualmente el espacio."),
        ("¿Cómo evito que el azogue se pique con la humedad?",
         "Elige espejos con bordes sellados específicamente diseñados para baño. Mantén buena ventilación durante y después de la ducha (extractor o ventana). Los espejos baratos sin sello se pican en 1-2 años de uso intensivo."),
        ("¿Los espejos con aumento sirven para todo el baño?",
         "No reemplazan al espejo principal: son complementarios. Un espejo X3 o X5 es ideal para maquillaje, afeitado y cuidado detallado de la piel. Se instala junto al espejo grande, generalmente sobre un brazo extensible."),
        ("¿Es difícil colgar un espejo grande?",
         "Para espejos sobre 60x60 cm recomendamos fijación con tarugos y tornillos al muro sólido (no tabique liviano). Los espejos del catálogo Victtorino incluyen sistema de anclaje. Cualquier maestro con experiencia básica los instala en 30 minutos."),
    ],
    118: [  # Shower
        ("¿Qué medida de shower door es la más común?",
         "Las medidas 80x80 cm y 90x90 cm son las más vendidas en Chile. El 80x80 funciona perfecto en baños estándar y departamentos. El 90x90 es más cómodo para personas altas o que prefieren mayor espacio de movimiento."),
        ("¿Cuál es más práctico: shower door curvo o recto?",
         "El shower door curvo aprovecha mejor las esquinas y libera espacio de circulación en el baño. El recto se ve más arquitectónico y elegante, ideal para baños amplios. Curvos suelen ser más populares en Chile por el tipo de planta común."),
        ("¿Necesito un receptáculo antideslizante?",
         "Es muy recomendable, especialmente con niños, adultos mayores o cualquiera que se duche con prisa. Los receptáculos modernos vienen con superficie texturizada o tratamiento antideslizante de fábrica, sin necesidad de stickers adicionales."),
        ("¿El vidrio templado es seguro?",
         "Sí. El vidrio templado se procesa térmicamente para resistir golpes 4-5 veces más que el vidrio común. Si llega a romperse, se desintegra en partículas pequeñas sin filos cortantes peligrosos. Es el estándar de seguridad en shower doors modernos."),
        ("¿Cuánto demora instalar un shower door?",
         "Un maestro con experiencia en mamparas instala un shower door 80x80 o 90x90 en 3-5 horas. Incluye preparación del receptáculo, sellado con silicona y ajuste de perfiles. Requiere muros sólidos para fijación de las bisagras."),
    ],
    112: [  # Accesorios
        ("¿Vale la pena comprar accesorios de baño en set completo?",
         "Sí, por dos razones: ahorras 15-25% versus comprar pieza por pieza, y garantizas que todas tengan el mismo acabado y línea de diseño (clave para que el baño se vea armónico). Los sets de 5-6 piezas son los más vendidos."),
        ("¿Los accesorios plásticos duran lo mismo que los de metal?",
         "No. Los accesorios plásticos baratos se decoloran y se vuelven quebradizos en 1-2 años. El acero inoxidable o latón cromado de calidad mantiene su aspecto durante años en el ambiente húmedo del baño."),
        ("¿Necesito hacer perforaciones para instalar accesorios?",
         "La mayoría se fijan con tornillos y tarugos al muro. Algunos modelos modernos usan adhesivos de alta resistencia para no perforar, ideal para arriendos o quienes no quieren tocar el muro. La instalación tarda 15-30 minutos por pieza."),
        ("¿Qué accesorios son indispensables en un baño?",
         "El mínimo recomendado: toallero principal, portarrollos, jabonera (o dispensador), gancho para colgar y barra para toalla de manos. Para baños familiares se suma un toallero adicional y un basurero con pedal."),
        ("¿Cómo mantengo los accesorios limpios?",
         "Paño suave con agua tibia para uso diario. Una vez por semana, agua con jabón neutro. Evitar limpiadores con cloro concentrado o partículas abrasivas que rayan el acabado cromado o plateado."),
    ],
    114: [  # Dispensador
        ("¿Es más económico un dispensador con jabón a granel?",
         "Sí, entre 30% y 50% más económico que comprar botellas individuales de jabón líquido. En baños comerciales el ahorro paga el dispensador en pocos meses; en hogares familiares, en menos de un año."),
        ("¿Los dispensadores con sensor valen la pena?",
         "Para baños públicos, oficinas o restaurantes son una excelente inversión: higiene sin contacto, mejor imagen y control automático de dosis. Para hogar son más una cuestión de gusto que de necesidad."),
        ("¿Qué dispensador elegir para baño público con mucho flujo?",
         "Capacidad de 1 litro o más, fijación al muro firme y material resistente a vandalismo. Para papel higiénico, modelos para rollo industrial reducen la frecuencia de recargas y evitan robos del rollo."),
        ("¿Es fácil rellenar los dispensadores?",
         "Los modelos manuales se rellenan abriendo la tapa superior y vaciando el bidón de jabón a granel. Toma 30 segundos. Los modelos automáticos con sensor incluyen indicador de nivel para saber cuándo recargar."),
        ("¿El dispensador funciona con cualquier jabón líquido?",
         "Sí con jabones líquidos comunes (manos, gel sanitizante, alcohol gel). Para jabones muy espesos o cremas se requiere modelo específico. Evitar jabones con partículas exfoliantes que tapan el mecanismo."),
    ],
    143: [  # Agarraderas
        ("¿A qué altura instalar una agarradera de baño?",
         "Para la ducha, entre 80 y 100 cm desde el piso, en posición horizontal o inclinada 45°. Junto al WC, a 70-80 cm de altura. Lo ideal es probarlas con la persona que más las va a usar antes de fijar definitivamente."),
        ("¿Las agarraderas solo sirven para adultos mayores?",
         "No. Son útiles para niños que aprenden a ducharse solos, mujeres embarazadas, personas en recuperación de lesiones y cualquier adulto que valore seguridad extra. Son un seguro silencioso para toda la familia."),
        ("¿Qué medida de barra de seguridad necesito?",
         "30 cm para apoyo puntual en zonas chicas (junto al WC), 40-60 cm para apoyo firme en la ducha, 90+ cm para apoyo continuo en duchas amplias. Barras esquineras con 3 apoyos son lo más seguro."),
        ("¿Puedo instalar agarraderas en cualquier muro?",
         "Idealmente sobre muro de albañilería sólida con tornillos y tarugos. En tabiques de yeso-cartón se requieren fijaciones químicas o anclajes específicos. Nunca instalar con solo adhesivos en barras de seguridad reales."),
        ("¿El acero inoxidable resiste la humedad del baño?",
         "Sí, es el material recomendado para baños húmedos. No se oxida ni decolora con el vapor permanente. El acabado pulido o cepillado se mantiene como nuevo durante años con limpieza básica."),
    ],
    144: [  # Sifones
        ("¿Por qué huele mal el desagüe de mi baño?",
         "Generalmente es porque el sifón está seco, dañado o mal instalado. El sifón mantiene una columna de agua que bloquea los olores del alcantarillado. Cambiar un sifón viejo por uno nuevo elimina malos olores en minutos."),
        ("¿Cada cuánto hay que cambiar el sifón?",
         "Un sifón plástico de calidad dura 5-10 años en uso doméstico normal. Si notas filtraciones bajo el lavamanos o lavaplatos, malos olores persistentes, o el agua tarda en bajar, es momento de cambiarlo aunque no haya pasado tanto tiempo."),
        ("¿Qué diámetro de sifón necesito?",
         "Para lavamanos: 1 1/4 pulgada (el estándar). Para lavaplatos: 1 1/2 pulgada para uso doméstico, hasta 3 1/2 pulgadas (114 mm) para lavaplatos modernos. Para ducha y tina: depende del receptáculo, generalmente 90 mm."),
        ("¿Es complicado cambiar un sifón?",
         "No. Es una de las reparaciones más sencillas del baño y cocina: cerrar la llave de paso, desconectar el sifón viejo a mano, conectar el nuevo con su empaque. Cualquier persona con destornillador puede hacerlo en 20 minutos."),
        ("¿Los sifones plásticos duran tanto como los metálicos?",
         "Los plásticos modernos de calidad resisten muy bien la corrosión química (mejor que el metal en algunos casos). Los metálicos resisten mejor los golpes accidentales. Para uso doméstico estándar, los plásticos son la opción más popular y económica."),
    ],
    145: [  # WC e Inodoros
        ("¿Mi WC se llena solo, qué hago?",
         "Es la falla más común: la válvula de carga no cierra bien y deja entrar agua continuamente. Reemplazar la válvula con un kit completo de estanque (carga, descarga y fijaciones) soluciona el problema en 30 minutos sin llamar al plomero."),
        ("¿Cuánto dura una válvula de WC?",
         "Las válvulas de calidad duran 5-8 años en uso doméstico normal. Las baratas pueden fallar en 1-2 años. Si tu WC tiene más de 5 años y nunca se ha cambiado el mecanismo interno, probablemente es momento."),
        ("¿Las llaves temporizadas valen la pena para mi negocio?",
         "Sí, especialmente en baños públicos: ahorran 30-60% del consumo de agua versus llaves comunes y eliminan el problema de gente que olvida cerrar la llave. El ROI suele ser de meses, no años."),
        ("¿Qué incluye un kit completo de estanque WC?",
         "Un kit completo trae: válvula de carga (la que entra agua al estanque), válvula de descarga (la que libera al jalar) y fijaciones (tornillería y empaques). Reemplaza todo el mecanismo interno en una sola compra."),
        ("¿Puedo cambiar componentes de WC yo mismo?",
         "Sí, la mayoría de los cambios internos son accesibles: tapas, válvulas, mecanismos de descarga. Solo requiere cerrar la llave de paso del estanque y seguir instrucciones básicas. Para cambiar el WC completo sí recomendamos gasfíter."),
    ],
}


def generar_schema(faqs):
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": p,
             "acceptedAnswer": {"@type": "Answer", "text": r}}
            for p, r in faqs
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'


# Aplicar a cada categoría
print(f"Inyectando FAQPage schema en {len(FAQS)} categorías...\n")
ok = 0
for cat_id, faqs in FAQS.items():
    # Leer descripción actual
    r = requests.get(f"{WC}/wp-json/wc/v3/products/categories/{cat_id}",
                     params=P, timeout=30)
    actual = r.json().get("description", "")
    if "application/ld+json" in actual:
        print(f"  cat {cat_id} ya tiene schema, salto")
        continue
    schema_html = generar_schema(faqs)
    nueva = actual + "\n\n" + schema_html
    for n in range(1, 4):
        try:
            r2 = requests.put(f"{WC}/wp-json/wc/v3/products/categories/{cat_id}",
                              json={"description": nueva}, params=P, timeout=120)
            if r2.status_code == 503:
                time.sleep(6 * n); continue
            if r2.status_code >= 400:
                print(f"  cat {cat_id} ERR {r2.status_code}")
                break
            d = r2.json()
            # Verificar si el script quedó
            tiene_script = "application/ld+json" in d.get("description", "")
            print(f"  cat {cat_id:3} -> {'OK' if tiene_script else 'WP filtró el script'}")
            if tiene_script:
                ok += 1
            break
        except Exception as e:
            time.sleep(4 * n)
    time.sleep(1)

print(f"\n{ok}/{len(FAQS)} categorías con schema JSON-LD")
