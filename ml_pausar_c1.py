# -*- coding: utf-8 -*-
"""Pausa las publicaciones de catálogo duplicadas de C1 (ml_pausar_c1_final.json).
PUT /items/{id} status=paused. Refresh token transparente, rate-limit, reporte."""
import json, time, random, requests
from pathlib import Path
ROOT=Path(r"C:\Users\dell\victtorino")
CID='3959231945649654'; CSEC='PVvpcsugyGfL7DPeQTVi71iCbRkqdNtG'
TF=ROOT/'tokens_cuenta1.json'
BASE='https://api.mercadolibre.com'

tok=json.loads(TF.read_text())
def refresh():
    r=requests.post(f'{BASE}/oauth/token',data={'grant_type':'refresh_token','client_id':CID,'client_secret':CSEC,'refresh_token':tok['refresh_token']},timeout=30)
    r.raise_for_status(); d=r.json()
    tok['access_token']=d['access_token']; tok['refresh_token']=d.get('refresh_token',tok['refresh_token'])
    TF.write_text(json.dumps(tok,indent=2)); print('  token C1 refrescado')

items=json.load(open(ROOT/'ml_pausar_c1_final.json'))
print(f'A pausar en C1: {len(items)} publicaciones')
ok=[]; already=[]; fail=[]
for i,it in enumerate(items,1):
    iid=it['item']
    for intento in range(1,4):
        r=requests.put(f'{BASE}/items/{iid}',headers={'Authorization':'Bearer '+tok['access_token'],'Content-Type':'application/json'},json={'status':'paused'},timeout=30)
        if r.status_code==401 and intento==1: refresh(); continue
        if r.status_code==429:
            w=float(r.headers.get('Retry-After',0)) or 2**intento; time.sleep(w+random.random()); continue
        break
    if r.status_code==200:
        st=r.json().get('status')
        (ok if st=='paused' else already).append(iid)
    else:
        try: msg=r.json().get('message') or r.text[:80]
        except: msg=r.text[:80]
        fail.append((iid,r.status_code,msg))
    if i%20==0: print(f'  {i}/{len(items)} procesados... (ok {len(ok)}, fail {len(fail)})')
    time.sleep(0.2)
print()
print('==== RESULTADO ====')
print('Pausadas OK:',len(ok))
print('Ya estaban paused/otro estado:',len(already))
print('Fallidas:',len(fail))
for f in fail[:15]: print('  FAIL',f[0],f[1],f[2])
json.dump({'ok':ok,'already':already,'fail':fail},open(ROOT/'ml_pausar_c1_resultado.json','w'),indent=2)
