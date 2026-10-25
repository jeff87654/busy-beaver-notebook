from pathlib import Path
import json,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from lastfive_decider_cps import job
from lastfive_decider_cps_verify import verify
machines=Path('discovery_holdouts.txt').read_text().splitlines()
settings=[(h,b,w)for h in(0,2,8,'lru')for b in(6,8,12)for w in(2*b+1,3*b)]
settings += [(h,b,3*b)for h in(16,32)for b in(8,12,16)]
results=[];started=time.monotonic()
with ThreadPoolExecutor(max_workers=2)as pool:
 futures=[]
 for c in(13,15):
  for i,(h,b,w)in enumerate(settings):
   p={'id':f'C{c:02}','machine':machines[c-1],'setting':24+i,'history':h,'block':b,'window':w,'max_steps':2000000,'max_configs':50000,'max_edges':100000,'timeout':6}
   futures.append(pool.submit(job,p))
 for f in as_completed(futures):
  r=f.result()
  if 'certificate'in r:
   try:r['independent_verification']=verify(json.loads(Path(r['certificate']).read_text()))
   except Exception as e:r['independent_verification']={'status':'rejected_or_inconclusive','reason':repr(e)}
  results.append(r)
  Path('lastfive_decider_cps_deep.json').write_text(json.dumps({'engine':'Standalone CPS with corrected finite history','settings':settings,'elapsed_seconds':time.monotonic()-started,'results':results},indent=2))
  print(r.get('id'),r.get('setting'),r['status'],r.get('counts'),flush=True)
print('done',len(results),'seconds',time.monotonic()-started)
