# -*- coding: utf-8 -*-
"""Plan final de precios Falabella con COSTO VALIDADO (validacion_costos.xlsx).
Sube SOLO lo seguro: producto con competidor TAUMM + stock + margen >= 20% + costo
confianza ALTA/MEDIA + actualmente sobreprecio. El resto -> lista flag para revision."""
import json, re, glob, openpyxl

def load(f):
    raw = open(f, encoding='utf-8').read().strip()
    d = json.loads(raw)
    if isinstance(d, str): d = json.loads(d)
    return d

# stock/precio admin
admin = {}
for f in sorted(glob.glob('admin_p*.json')):
    d = load(f); rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
    for r in rows: admin[r['seller']] = r

# costo validado
wv = openpyxl.load_workbook('validacion_costos.xlsx', data_only=True).active
rv = list(wv.iter_rows(values_only=True)); Hv = rv[0]
ic=Hv.index('Codigo'); icu=Hv.index('COSTO A USAR'); icf=Hv.index('Confianza'); idd=Hv.index('Descripcion')
cost = {r[ic]: {'c': r[icu], 'conf': r[icf], 'desc': r[idd]} for r in rv[1:] if r[ic] and isinstance(r[icu],(int,float))}

# competidores TAUMM
taumm=[]
for f in sorted(glob.glob('taumm_[0-9].json')):
    try: taumm += load(f)
    except: pass
comp=[c for c in taumm if 'Trade' not in c.get('seller','')]
MOD=['NOTTE','COLOMBA','DOMENICA','VANDER','MODERN','BONN','SWERTT','ANTONELLA','MILAN','PROFESIONAL','TEMPORIZADA','CISNE','VERTICAL','ALTO','BIDET','MONOBLOCK','LAVACOPA','EXTRAIBLE','CUELLO']
TIP=['LAVAPLATO','LAVATORIO','LAVAMANOS','DUCHA','TINA','BIDET','LAVACOPA','JARDIN','ANGULAR','DISPENSADOR','RECEPTACULO','FLUXOMETRO','BARRA']
MS=set(MOD)
def tk(n):
    n=n.upper(); s=set()
    for m in MOD:
        if m in n: s.add(m)
    for t in TIP:
        if t in n: s.add(t)
    return s
def r990(x):
    x=int(round(x)); return (x//1000)*1000+990 if x>=1000 else max(0,x)
def best_comp(desc):
    mt=tk(desc); my=mt&MS; b=None
    for c in comp:
        ct=tk(c['name'])
        if mt and len(mt&ct)>=2 and (not my or (my&ct)):
            if b is None or c['price']<b['price']: b=c
    return b

YA_SUBIDOS={'010701007-T','020101010-T','020101011-T','020101001-T','020101002-T','020101003-T','040303003-T','040203017-C','040201006-T','040202005-T'}

upload=[]; flag=[]
for sku,a in admin.items():
    if not (a.get('stock') and a['stock']>0): continue
    if sku in YA_SUBIDOS: continue
    cv=cost.get(sku)
    cur=a.get('special') or a.get('price') or 0
    desc=(cv['desc'] if cv else a.get('name','')) or ''
    rec={'sku':sku,'desc':str(desc)[:32],'cur':cur,'stock':a['stock'],'ads':a.get('sponsored')}
    if not cv:
        rec['motivo']='sin costo validado'; flag.append(rec); continue
    civa=cv['c']*1.19
    b=best_comp(str(desc))
    if not b:
        rec['motivo']='sin competidor TAUMM'; flag.append(rec); continue
    venta=r990(b['price']-1000)
    margen=1-civa/venta if venta else -1
    rec.update({'venta':venta,'comp':b['price'],'margen':margen,'conf':cv['conf']})
    if margen>=0.20 and cv['conf'] in ('ALTA','MEDIA') and cur>venta*1.05:
        upload.append(rec)
    else:
        rec['motivo']=f"margen {margen*100:.0f}% / {cv['conf']}" + ('' if cur>venta else ' / no sobreprecio')
        flag.append(rec)

print('=== SUBIR (seguro) ===', len(upload))
for u in sorted(upload,key=lambda z:-z['cur']):
    print(f"  {u['sku']:13} stk{u['stock']:>3} hoy{u['cur']:>8,} -> {u['venta']:>7,} (m{u['margen']*100:.0f}% {u['conf']}){'  ADS' if u['ads'] else ''}  {u['desc']}")
print('\n=== FLAG (revision) ===', len(flag))
for fl in flag[:60]:
    print(f"  {fl['sku']:13} hoy{fl.get('cur',0):>8,}  {fl.get('motivo','')[:34]:34} {fl['desc']}")

json.dump({'upload':upload,'flag':flag}, open('plan_final.json','w',encoding='utf-8'), ensure_ascii=False)
