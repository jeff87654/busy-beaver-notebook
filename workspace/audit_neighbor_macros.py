import json,time
from macro import simulate_macro
from sim import parse
start=time.monotonic()
data=json.load(open('audit_neighbors.json'))
rows=sorted((r for r in data['results'] if r['status']=='ops'),key=lambda r:r['steps'],reverse=True)[:12]
out=[]
for r in rows:
 if time.monotonic()-start>35:break
 checks=[]
 for k in (2,3,4):
  if time.monotonic()-start>35:break
  result=simulate_macro(parse(r['machine']),k,100000)
  checks.append({'k':k,'status':result[0],'steps':result[1],'ones':result[2],'ops':result[3]})
  if result[0] in ('halt','infinite'):break
 out.append({'machine':r['machine'],'checks':checks})
 if any(c['status']=='halt' for c in checks):print(out[-1],flush=True)
json.dump({'elapsed_seconds':time.monotonic()-start,'results':out},open('audit_neighbor_macros.json','w'),indent=2)
print('Probed',len(out),'neighbors in',time.monotonic()-start,'seconds',flush=True)
