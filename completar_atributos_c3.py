import json, requests, time, re
from pathlib import Path

tokens = json.loads(Path('tokens_cuenta3.json').read_text())
h = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}
base = 'https://api.mercadolibre.com'
me = requests.get(f"{base}/users/me", headers=h).json()
uid = me["id"]

# Cargar todos los items activos
print('Cargando items activos...')
all_ids = []
offset = 0
while True:
    r = requests.get(f'{base}/users/{uid}/items/search', headers=h, params={'offset': offset, 'limit': 50}).json()
    all_ids.extend(r.get('results', []))
    offset += 50
    if offset >= r.get('paging', {}).get('total', 0): break
    time.sleep(0.1)

items = []
for i in range(0, len(all_ids), 20):
    chunk = ','.join(all_ids[i:i+20])
    r = requests.get(f'{base}/items', headers=h, params={'ids': chunk}).json()
    for entry in r:
        if entry.get('code') == 200 and entry['body'].get('status') == 'active':
            items.append(entry['body'])
    time.sleep(0.2)

print(f'Items activos: {len(items)}')

cat_cache = {}
def cat_attrs(cat_id):
    if cat_id in cat_cache:
        return cat_cache[cat_id]
    data = requests.get(f'{base}/categories/{cat_id}/attributes', headers=h).json() or []
    cat_cache[cat_id] = {a['id']: a for a in data}
    time.sleep(0.15)
    return cat_cache[cat_id]

skip_dims = {
    'BATHTUBS_FAUCET_HEIGHT','BATHTUBS_FAUCET_LENGTH','BATHTUBS_FAUCET_WIDTH',
    'BIDET_FAUCET_WIDTH','HANDHELD_SHOWER_LENGTH','MAX_WATER_PRESSURE',
    'SINK_FAUCET_HEIGHT','SINK_FAUCET_LENGTH','SINK_FAUCET_WIDTH',
    'INSTALLATION_HOLE_DIAMETER','VALVE_WEIGHT','PACKAGE_HEIGHT',
    'PACKAGE_LENGTH','PACKAGE_WIDTH','PACKAGE_WEIGHT',
}

def deducir_valor(attr_id, titulo, cat_map):
    t = titulo.lower()
    a = cat_map.get(attr_id, {})
    allowed = {v['name'].lower(): v for v in a.get('values', []) or a.get('allowed_values', [])}

    def match(candidates):
        for c in candidates:
            if c.lower() in allowed:
                v = allowed[c.lower()]
                return v.get('id'), v.get('name', c)
        return None, None

    if attr_id in ('PRODUCT_DATA_SOURCE', 'PRODUCT_ORIGIN'):
        vid, vname = match(['Importado', 'Nacional', 'Fabricante'])
        return vid, vname or 'Importado'
    if attr_id in ('MATERIALS', 'MATERIAL'):
        if any(x in t for x in ['inox', 'inoxidable', 'acero']):
            vid, vname = match(['Acero inoxidable', 'Acero'])
            return vid, vname or 'Acero inoxidable'
        if any(x in t for x in ['plastico', 'plastico', 'abs', 'pvc']):
            vid, vname = match(['Plastico', 'ABS', 'PVC'])
            return vid, vname or 'Plastico'
        if 'vidrio' in t:
            return match(['Vidrio']) or (None, 'Vidrio')
        if any(x in t for x in ['laton', 'laton', 'bronce']):
            vid, vname = match(['Laton', 'Bronce'])
            return vid, vname or 'Laton'
        if any(x in t for x in ['goma', 'caucho']):
            vid, vname = match(['Goma', 'Caucho'])
            return vid, vname or 'Goma'
        if any(x in t for x in ['cromo', 'cromado']):
            return None, 'Cromado'
        return None, 'Acero inoxidable'
    if attr_id in ('FINISH', 'ACABADO'):
        if 'plateado' in t: return match(['Plateado', 'Cromado']) or (None, 'Plateado')
        if 'negro' in t: return match(['Negro', 'Mate negro']) or (None, 'Negro')
        if 'blanco' in t: return match(['Blanco']) or (None, 'Blanco')
        if 'dorado' in t: return match(['Dorado']) or (None, 'Dorado')
        return None, 'Cromado'
    if attr_id == 'COLOR':
        if 'negro' in t: return match(['Negro']) or (None, 'Negro')
        if 'blanco' in t: return match(['Blanco']) or (None, 'Blanco')
        if 'dorado' in t: return match(['Dorado']) or (None, 'Dorado')
        return None, 'Plateado'
    if attr_id == 'VOLTAGE':
        if any(x in t for x in ['luz', 'led', 'luces', 'espejo']):
            vid, vname = match(['220V', '220 V', '100-240V'])
            return vid, vname or '220V'
        return None, 'No aplica'
    if attr_id in ('INSTALLATION_PLACEMENT', 'LUGAR_COLOCACION'):
        if 'urinario' in t: return None, 'Urinario'
        if any(x in t for x in ['lavaplatos', 'bacha']): return None, 'Cocina'
        if any(x in t for x in ['lavatorio', 'lavamanos']): return None, 'Bano'
        if any(x in t for x in ['tina', 'banera']): return None, 'Bano'
        return None, 'Bano'
    if attr_id in ('SOAP_CONSISTENCY', 'CONSISTENCIAS_PRODUCTO'):
        vid, vname = match(['Liquido', 'Liquido'])
        return vid, vname or 'Liquido'
    if attr_id in ('DISPENSING_TYPE', 'TIPO_DOSIFICACION'):
        vid, vname = match(['Presion', 'Push'])
        return vid, vname or 'Presion'
    if attr_id in ('RECOMMENDED_INSTALLATION_ROOMS',):
        vid, vname = match(['Bano', 'Bano'])
        return vid, vname or 'Bano'
    if attr_id in ('SIZE', 'TAMANO', 'TAMA_O'):
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:"|pulgadas?|mm|cm)', t)
        if m: return None, m.group(1)
        m = re.search(r'(\d/\d)', t)
        if m: return None, m.group(1)
    if 'DIAMETER' in attr_id or 'DIAMETRO' in attr_id:
        m = re.search(r'(\d/\d)', t)
        if m: return None, m.group(1)
        m = re.search(r'(\d+)\s*mm', t)
        if m: return None, m.group(1)
    if 'WATER_TEMP' in attr_id:
        vid, vname = match(['Fria y caliente', 'Caliente y fria'])
        return vid, vname or 'Fria y caliente'
    if attr_id == 'ITEM_CONDITION':
        vid, vname = match(['Nuevo'])
        return vid, vname or 'Nuevo'
    return None, None


aplicados = errores = saltados = items_procesados = 0

for item in items:
    cat = item.get('category_id', '')
    titulo = item.get('title', '')
    iid = item['id']
    attrs_actuales = {a['id']: a.get('value_name', '') for a in item.get('attributes', [])}

    cat_map = cat_attrs(cat)
    attrs_enviar = []

    for attr_id, attr_def in cat_map.items():
        if attr_id in skip_dims: continue
        if attr_id in attrs_actuales and attrs_actuales[attr_id]: continue
        if attr_def.get('tags', {}).get('read_only'): continue

        vid, val = deducir_valor(attr_id, titulo, cat_map)
        if val:
            entry = {'id': attr_id, 'value_name': str(val)}
            if vid: entry['value_id'] = vid
            attrs_enviar.append(entry)

    if not attrs_enviar:
        saltados += 1
        continue

    r = requests.put(f'{base}/items/{iid}', headers=h, json={'attributes': attrs_enviar})
    if r.ok:
        aplicados += len(attrs_enviar)
        items_procesados += 1
    else:
        errores += 1
    time.sleep(0.3)

print(f'Items procesados:    {items_procesados}')
print(f'Atributos aplicados: {aplicados}')
print(f'Items sin cambios:   {saltados}')
print(f'Errores:             {errores}')
