# -*- coding: utf-8 -*-
"""
Mejora descripciones de items NO-catalogo con descripcion corta o generica.
Genera descripcion estructurada basada en titulo + atributos.
Umbral: descripciones con menos de 350 caracteres o sin descripcion.
"""
import json, requests, time
from pathlib import Path

base = 'https://api.mercadolibre.com'
UMBRAL_CHARS = 350

# ==============================================================
# Generador de descripcion
# ==============================================================
def generar_descripcion(title, attrs_dict, categoria):
    """Genera descripcion HTML estructurada basada en titulo y atributos."""

    brand = attrs_dict.get('BRAND', '')
    material = attrs_dict.get('MATERIAL') or attrs_dict.get('MATERIALS', '')
    color = attrs_dict.get('COLOR', '')
    finish = attrs_dict.get('FINISH', '') or attrs_dict.get('ACABADO', '')
    condition = attrs_dict.get('ITEM_CONDITION', 'Nuevo')
    width = attrs_dict.get('WIDTH', '')
    length = attrs_dict.get('LENGTH', '')
    depth = attrs_dict.get('DEPTH', '')
    voltage = attrs_dict.get('VOLTAGE', '')
    install = attrs_dict.get('INSTALLATION_TYPES', '') or attrs_dict.get('INSTALLATION_PLACEMENT', '')
    line = attrs_dict.get('LINE', '')

    t = title.lower()

    # Determinar tipo de producto para intro contextualizada
    if any(x in t for x in ['lavaplatos', 'bacha']):
        tipo = 'lavaplatos'
        intro = (f"{title} fabricado en {material or 'acero inoxidable'} de alta calidad, "
                 f"ideal para cocinas modernas y funcionales. "
                 f"Su resistencia a la corrosion y facil limpieza lo hacen la opcion perfecta para el uso diario.")
        beneficios = [
            "Acero inoxidable duradero y resistente a la corrosion",
            "Facil de limpiar y mantener",
            "Diseno moderno adaptable a cualquier cocina",
            "Instalacion sencilla"
        ]
    elif any(x in t for x in ['espejo', 'mirror']):
        tipo = 'espejo'
        intro = (f"{title} que combina funcionalidad y estetica para tu bano. "
                 f"Su acabado {finish or 'de alta calidad'} aporta elegancia y luminosidad al espacio.")
        beneficios = [
            "Diseno elegante y moderno",
            "Facil instalacion en pared",
            "Vidrio de alta calidad con bordes pulidos",
            "Ideal para banos y vestidores"
        ]
        if 'led' in t:
            beneficios.insert(0, "Iluminacion LED integrada de bajo consumo")
    elif any(x in t for x in ['receptaculo', 'ducha', 'shower']):
        tipo = 'receptaculo ducha'
        intro = (f"{title} de {material or 'acero esmaltado'}, disenado para brindar comodidad y seguridad en tu bano. "
                 f"Su superficie antideslizante y construccion robusta garantizan durabilidad y seguridad.")
        beneficios = [
            "Superficie antideslizante para mayor seguridad",
            "Material resistente a la humedad y temperatura",
            "Facil instalacion y mantenimiento",
            "Compatibilidad con desagues estandar"
        ]
    elif any(x in t for x in ['llave', 'grifo', 'mezcladora', 'monomando']):
        tipo = 'griferia'
        intro = (f"{title} fabricada en {material or 'laton cromado'} de alta durabilidad. "
                 f"Su diseno {finish or 'cromado'} aporta elegancia y la tecnologia interna garantiza larga vida util.")
        beneficios = [
            f"Material {material or 'laton'} de alta durabilidad",
            "Acabado resistente a manchas y oxidacion",
            "Diseno ergonomico para uso comodo",
            "Compatible con instalaciones estandar"
        ]
    elif any(x in t for x in ['dispensador', 'jabonera']):
        tipo = 'dispensador'
        intro = (f"{title} practico y elegante para tu bano o cocina. "
                 f"Su diseno {finish or 'moderno'} complementa cualquier decoracion mientras mantiene el jabon siempre accesible.")
        beneficios = [
            "Facil de rellenar y usar",
            "Material resistente y duradero",
            "Adhesivo o de montaje en pared",
            "Capacidad generosa para uso continuo"
        ]
    elif any(x in t for x in ['flexible', 'manguera']):
        tipo = 'flexible'
        intro = (f"{title} de alta resistencia para instalaciones de agua. "
                 f"Fabricado con materiales que garantizan hermeticidad y durabilidad en el tiempo.")
        beneficios = [
            "Resistente a la presion del agua",
            "Facil instalacion sin herramientas especiales",
            "Compatible con conexiones estandar",
            "Material anticorrosion"
        ]
    elif any(x in t for x in ['pack', 'kit', 'set', 'combo']):
        tipo = 'pack'
        intro = (f"{title}: la combinacion perfecta para equipar tu cocina o bano con todo lo necesario en una sola compra. "
                 f"Productos seleccionados por calidad y compatibilidad entre si.")
        beneficios = [
            "Ahorro vs comprar por separado",
            "Productos compatibles entre si",
            "Instalacion coordinated",
            "Calidad garantizada en todos los componentes"
        ]
    elif any(x in t for x in ['toalla', 'papel', 'higienico', 'rollo']):
        tipo = 'papel'
        intro = (f"{title} de alta absorcion para uso profesional o del hogar. "
                 f"Fabricado con materiales suaves y resistentes para mayor comodidad.")
        beneficios = [
            "Alta absorcion",
            "Suave al tacto",
            "Gran rendimiento por rollo",
            "Ideal para uso intensivo"
        ]
    elif any(x in t for x in ['desague', 'sifon', 'trampa']):
        tipo = 'desague'
        intro = (f"{title} de calidad para instalaciones de plomeria. "
                 f"Material resistente que garantiza estanqueidad y durabilidad en el tiempo.")
        beneficios = [
            "Material resistente a productos quimicos",
            "Instalacion sencilla",
            "Compatible con sistemas estandar",
            "Sello hermetico de larga duracion"
        ]
    else:
        tipo = 'accesorio'
        intro = (f"{title} de {material or 'alta calidad'} para el equipamiento de tu hogar. "
                 f"Fabricado con materiales seleccionados para garantizar durabilidad y funcionalidad.")
        beneficios = [
            f"Calidad {material or 'premium'}",
            "Diseno duradero",
            "Facil instalacion",
            "Garantia de satisfaccion"
        ]

    # Construir especificaciones tecnicas
    specs = []
    if material: specs.append(f"Material: {material}")
    if color: specs.append(f"Color: {color}")
    if finish and finish != color: specs.append(f"Acabado: {finish}")
    if width and length:
        if depth:
            specs.append(f"Dimensiones: {length} x {width} x {depth}")
        else:
            specs.append(f"Dimensiones: {length} x {width}")
    elif length:
        specs.append(f"Largo: {length}")
    if install: specs.append(f"Instalacion: {install}")
    if voltage and voltage != 'No aplica': specs.append(f"Voltaje: {voltage}")
    if brand and brand.lower() not in ('generico', 'generic', ''): specs.append(f"Marca: {brand}")
    if condition: specs.append(f"Condicion: {condition}")

    # Construir descripcion
    lines = []
    lines.append(intro)
    lines.append("")

    if specs:
        lines.append("Especificaciones tecnicas:")
        for s in specs:
            lines.append(f"- {s}")
        lines.append("")

    if beneficios:
        lines.append("Por que elegirlo:")
        for b in beneficios:
            lines.append(f"- {b}")
        lines.append("")

    lines.append("Enviamos a todo Chile. Consulta stock y tiempo de entrega.")

    return "\n".join(lines)


# ==============================================================
# Procesar una cuenta
# ==============================================================
def procesar_cuenta(nombre, token_file):
    print(f"\n{'='*50}")
    print(f"Procesando {nombre}")
    print('='*50)

    tokens = json.loads(Path(token_file).read_text())
    h = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}

    me = requests.get(f'{base}/users/me', headers=h).json()
    uid = me['id']

    # Obtener todos los items activos
    all_ids = []
    offset = 0
    while True:
        r = requests.get(f'{base}/users/{uid}/items/search', headers=h,
                         params={'offset': offset, 'limit': 50}).json()
        all_ids.extend(r.get('results', []))
        offset += 50
        if offset >= r.get('paging', {}).get('total', 0): break
        time.sleep(0.1)

    print(f"Items activos: {len(all_ids)}")

    mejoradas = 0
    ya_ok = 0
    catalogo = 0
    errores = 0

    for i in range(0, len(all_ids), 20):
        chunk = ','.join(all_ids[i:i+20])
        batch = requests.get(f'{base}/items', headers=h, params={'ids': chunk}).json()
        time.sleep(0.2)

        for entry in batch:
            if entry.get('code') != 200: continue
            b = entry['body']
            if b.get('status') != 'active': continue

            iid = b['id']
            title = b.get('title', '')

            # Saltar solo items de catalogo ML (catalog_product_id bloquea descripcion)
            # family_name es solo agrupacion de variantes, no bloquea descripcion
            if b.get('catalog_product_id'):
                catalogo += 1
                continue

            # Obtener descripcion actual
            time.sleep(0.15)
            desc_r = requests.get(f'{base}/items/{iid}/description', headers=h)
            if desc_r.status_code == 200:
                desc_text = desc_r.json().get('plain_text', '') or ''
            else:
                desc_text = ''

            # Solo mejorar si descripcion es corta o vacia
            if len(desc_text.strip()) >= UMBRAL_CHARS:
                ya_ok += 1
                continue

            # Extraer atributos
            attrs_dict = {}
            for attr in b.get('attributes', []):
                attrs_dict[attr['id']] = attr.get('value_name', '')

            categoria = b.get('category_id', '')
            nueva_desc = generar_descripcion(title, attrs_dict, categoria)

            # Aplicar descripcion: POST si vacia, PUT si ya existe
            time.sleep(0.2)
            method = 'put' if desc_text.strip() else 'post'
            r_desc = getattr(requests, method)(
                f'{base}/items/{iid}/description', headers=h,
                json={'plain_text': nueva_desc}
            )
            if r_desc.ok:
                mejoradas += 1
                print(f"  OK {iid}: {len(desc_text)} -> {len(nueva_desc)} chars - {title[:40]}")
            else:
                # Si POST fallo por descripcion existente, reintentar con PUT
                if r_desc.status_code in (400, 409) and method == 'post':
                    time.sleep(0.2)
                    r_retry = requests.put(f'{base}/items/{iid}/description', headers=h,
                                           json={'plain_text': nueva_desc})
                    if r_retry.ok:
                        mejoradas += 1
                        print(f"  OK {iid}: {len(desc_text)} -> {len(nueva_desc)} chars - {title[:40]}")
                        continue
                errores += 1
                try:
                    err_msg = r_desc.json().get('message', '')[:80]
                except Exception:
                    err_msg = r_desc.text[:80]
                if 'catalog' in err_msg.lower() or 'not modif' in err_msg.lower():
                    catalogo += 1
                else:
                    print(f"  ERR {iid}: {err_msg}")

    print(f"\n  Mejoradas:   {mejoradas}")
    print(f"  Ya OK:       {ya_ok}")
    print(f"  Catalogo:    {catalogo}")
    print(f"  Errores:     {errores}")
    return mejoradas


# ==============================================================
# Ejecutar en las 3 cuentas
# ==============================================================
t1 = procesar_cuenta('C1 - PREMIUMGRIFERIAS1', 'tokens_cuenta1.json')
t2 = procesar_cuenta('C2 - VICTTORINOFICIAL2', 'tokens_cuenta2.json')
t3 = procesar_cuenta('C3 - NOVAGRIFERIAS3',    'tokens_cuenta3.json')

print(f"\n{'='*50}")
print(f"TOTAL DESCRIPCIONES MEJORADAS: {t1 + t2 + t3}")
print(f"  C1: {t1} | C2: {t2} | C3: {t3}")
