# -*- coding: utf-8 -*-
"""Tabla completa de distintivos/pendientes con stock: precio hoy, costo (validado o
vigente), competidor conocido y recomendacion."""
import json, glob, openpyxl

def load(f):
    raw=open(f,encoding='utf-8').read().strip(); d=json.loads(raw); return json.loads(d) if isinstance(d,str) else d

admin={}
for f in sorted(glob.glob('admin_p*.json')):
    d=load(f); rows=d['rows'] if isinstance(d,dict) and 'rows' in d else d
    for r in rows: admin[r['seller']]=r

# costo: validacion (mejor) -> vigente
ws=openpyxl.load_workbook('validacion_costos.xlsx',data_only=True).active
rv=list(ws.iter_rows(values_only=True)); H=rv[0]
val={r[H.index('Codigo')]:r[H.index('COSTO A USAR')] for r in rv[1:] if r[H.index('Codigo')] and isinstance(r[H.index('COSTO A USAR')],(int,float))}
vig=load('costos_vigentes.json')
def costo(sku):
    if sku in val: return val[sku],'val'
    if sku in vig and vig[sku].get('vig'): return vig[sku]['vig'],'vig'
    return None,None

# competidor conocido (de busquedas manuales)
COMP={'010502005-T':229000,'010501022-T':169990,'010201001-T':44990,'010102001-T':16990}
def r990(x): x=int(round(x)); return (x//1000)*1000+990 if x>=1000 else max(0,x)

done=set(['010701007-T','020101010-T','020101011-T','020101001-T','020101002-T','020101003-T','040303003-T','040203017-C','040201006-T','040202005-T','040303004-T','010701001-T','010205002-T','010104003-T','010301011-T','020103006-T','010301003-T','030102002-T','030102003-T','030101002-T','010104002-T','030102004-T','010301010-T','010301009-T','020301001-T','210000990-T','020202008-T','010704002-T','030101009-T','010602002-T','020203001-T','010103002-T','010301001-T','040302001-T','010403001-T','010603003-T','010103003-T','040301001-T','040202001-T','020102002-T','010701008-T','020102001-T','040201001-T','020103001-T','020201003-T','010102002-T'])
pend=[(s,a) for s,a in admin.items() if a.get('stock') and a['stock']>0 and s not in done]

rows=[]
for s,a in pend:
    cur=a.get('special') or a.get('price') or 0
    c,src=costo(s)
    civa=c*1.19 if c else None
    comp=COMP.get(s)
    if comp:
        rec=r990(comp-1000); base='competidor'
    elif civa:
        fac=1.8 if cur>=40000 else 2.3
        rec=r990(civa*fac); base='x%s'%fac
    else:
        rec=None; base='SIN DATO -> tu numero'
    margen=(1-civa/rec) if (civa and rec) else None
    rows.append({'sku':s,'name':(a.get('name') or '')[:34],'cur':cur,'stk':a['stock'],
                 'civa':int(civa) if civa else None,'comp':comp,'rec':rec,'base':base,
                 'margen':margen})

print('%-13s %8s %4s %8s %8s %9s %5s  %s'%('SKU','hoy','stk','costoIVA','compet','RECOM','marg','nombre'))
for r in sorted(rows,key=lambda z:-z['cur']):
    print('%-13s %8d %4d %8s %8s %9s %5s  %s'%(
        r['sku'],r['cur'],r['stk'],
        r['civa'] if r['civa'] else '-',
        r['comp'] if r['comp'] else '-',
        r['rec'] if r['rec'] else 'TU NUMERO',
        ('%d%%'%(r['margen']*100)) if r['margen'] else '-',
        r['name']))
json.dump(rows,open('tabla_distintivos.json','w',encoding='utf-8'),ensure_ascii=False)
