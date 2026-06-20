# -*- coding: utf-8 -*-
"""Cruza nuestras griferias (master) contra el catalogo TAUMM de competidores
(scrapeado de falabella) por tokens de modelo, y propone precio estandar."""
import json, re, glob, openpyxl

def load(f):
    raw = open(f, encoding='utf-8').read().strip()
    d = json.loads(raw)
    return json.loads(d) if isinstance(d, str) else d

taumm = []
for f in sorted(glob.glob('taumm_[0-9].json')):
    try: taumm += load(f)
    except Exception: pass
comp = [c for c in taumm if 'Trade' not in c.get('seller', '')]
print('TAUMM total:', len(taumm), '| competidores (no Trade):', len(comp))

MODELOS = ['NOTTE','COLOMBA','DOMENICA','VANDER','MODERN','BONN','SWERTT','ANTONELLA',
           'MILAN','PROFESIONAL','TEMPORIZADA','CISNE','VERTICAL','ALTO','BIDET',
           'MONOBLOCK','LAVACOPA','EXTRAIBLE','CUELLO']
TIPOS = ['LAVAPLATO','LAVATORIO','LAVAMANOS','DUCHA','TINA','BIDET','LAVACOPA','JARDIN','ANGULAR']

def toks(name):
    n = name.upper(); s = set()
    for m in MODELOS:
        if m in n: s.add(m)
    for t in TIPOS:
        if t in n: s.add(t)
    return s

ws = openpyxl.load_workbook('precios_descuentos_falabella.xlsx', data_only=True).active
rows = list(ws.iter_rows(values_only=True)); H = rows[0]
idesc = H.index('Descripcion'); iv = H.index('VENTA real (oferta)')
gri = [r for r in rows[1:] if re.search(r'MONOMANDO|LLAVE|GRIFO|MONOBLOCK|LAVACOPA', str(r[idesc]).upper())]
print('griferias en master:', len(gri))
print()

def r990(x):
    x = int(round(x)); return (x//1000)*1000+990 if x >= 1000 else max(0, x)

MODEL_SET = set(MODELOS)
alta, revisar, sinmatch = [], [], []
for r in gri:
    desc = str(r[idesc]); mt = toks(desc); my_model = mt & MODEL_SET
    best = None
    for c in comp:
        ct = toks(c['name'])
        if mt and len(mt & ct) >= 2:
            if best is None or c['price'] < best['price']:
                best = c; best_ct = ct
    if not best:
        sinmatch.append(r); continue
    est = r990(best['price'] - 1000)
    row = (r[0], desc[:30], r[iv], est, best['price'], best['name'][:30])
    # confianza alta si comparten el MISMO modelo especifico
    if my_model and (my_model & best_ct):
        alta.append(row)
    else:
        revisar.append(row)

def show(title, rows):
    print('\n=== %s (%d) ===' % (title, len(rows)))
    print('%-13s %-30s %8s %8s  %s' % ('codigo','desc','venta1.8','ESTANDAR','competidor'))
    for x in rows:
        print('%-13s %-30s %8s %8s  $%-7s %s' % (x[0], x[1], x[2], x[3], format(x[4], ',d'), x[5]))

show('CONFIANZA ALTA (mismo modelo)', alta)
show('A REVISAR (solo por tipo, modelo no confirmado)', revisar)
print('\nSin match:', [r[0] for r in sinmatch])
