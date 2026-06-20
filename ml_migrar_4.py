# -*- coding: utf-8 -*-
"""Completa migración de 4 productos C1->C3: crea los 3 restantes en C3 y pausa
los 4 originales en C1. El #1 (lavaplatos) ya fue creado (MLC4080595354)."""
import json,requests,time
CID='3959231945649654'; CSEC='PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG'
B='https://api.mercadolibre.com'
def load(f): return json.load(open(f))
t1=load('tokens_cuenta1.json'); t3=load('tokens_cuenta3.json')
def refresh(tok,f):
    d=requests.post(f'{B}/oauth/token',data={'grant_type':'refresh_token','client_id':CID,'client_secret':CSEC,'refresh_token':tok['refresh_token']},timeout=30).json()
    tok['access_token']=d['access_token']; tok['refresh_token']=d.get('refresh_token',tok['refresh_token']); json.dump(tok,open(f,'w'),indent=2)
def req(method,tok,f,path,**kw):
    for i in range(3):
        h={'Authorization':'Bearer '+tok['access_token']}
        if method=='POST' or method=='PUT': h['Content-Type']='application/json'
        r=requests.request(method,B+path,headers=h,timeout=40,**kw)
        if r.status_code==401 and i==0: refresh(tok,f); continue
        return r
    return r

# 3 restantes (el lavaplatos ya creado)
crear=[
 {'src':'MLC2189367944','pid':'MLC29037712','price':19856,'qty':5},
 {'src':'MLC1392687027','pid':'MLC23431506','price':13864,'qty':3},
 {'src':'MLC4063060722','pid':'MLC72728077','price':10201,'qty':2},
]
creados=[]; fallos=[]
for c in crear:
    s=req('GET',t1,'tokens_cuenta1.json',f"/items/{c['src']}").json()
    body={
     'catalog_product_id':c['pid'],'catalog_listing':True,
     'category_id':s.get('category_id'),
     'price':c['price'],'currency_id':'CLP','available_quantity':c['qty'],
     'listing_type_id':s.get('listing_type_id') or 'gold_pro','condition':'new','buying_mode':'buy_it_now',
     'sale_terms':[{'id':'WARRANTY_TYPE','value_name':'Garantía del vendedor'},{'id':'WARRANTY_TIME','value_name':'90 días'}],
     'shipping':{'mode':'me2','free_shipping':False,'local_pick_up':False}
    }
    r=req('POST',t3,'tokens_cuenta3.json','/items',json=body)
    if r.status_code in(200,201):
        j=r.json(); creados.append((c['src'],j.get('id'),j.get('status'))); print('CREADO',c['src'],'->',j.get('id'),j.get('status'))
    else:
        fallos.append((c['src'],r.status_code,json.dumps(r.json())[:200])); print('FALLO',c['src'],r.status_code,json.dumps(r.json())[:200])
    time.sleep(0.4)

# pausar los 4 originales en C1
print('\\n--- pausar originales en C1 ---')
originales=['MLC3906510406','MLC2189367944','MLC1392687027','MLC4063060722']
paused=[]; pfail=[]
for iid in originales:
    r=req('PUT',t1,'tokens_cuenta1.json',f'/items/{iid}',json={'status':'paused'})
    if r.status_code==200 and r.json().get('status')=='paused': paused.append(iid); print('PAUSADO',iid)
    else: pfail.append((iid,r.status_code,json.dumps(r.json())[:120])); print('no pausado',iid,r.status_code)
    time.sleep(0.3)

print('\\n==== RESUMEN ====')
print('Creados en C3:',len(creados),'/ 3   | fallos creacion:',len(fallos))
print('Originales C1 pausados:',len(paused),'/ 4   | fallos pausa:',len(pfail))
