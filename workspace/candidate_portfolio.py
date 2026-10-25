"""Block/macro portfolio for candidates C09-C16; cutoffs never decide a machine."""
import json,time,threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from ligocki_runner import run_machine

if __name__=='__main__':
 rows=json.loads(Path('candidate_manifest.json').read_text())[8:]
 jobs=[(r,k,back) for k,back in [(2,True),(3,True),(4,True),(6,True),(8,True),(1,True),(4,False),(2,False),(10,True),(12,True)] for r in rows]
 solved=set();lock=threading.Lock();start=time.monotonic()
 def work(job):
  r,k,back=job
  with lock:
   if r['id'] in solved:return {'id':r['id'],'status':'skipped','block_size':k}
  result=run_machine(r['machine'],timeout=6,max_loops=50000,block_size=k,no_backsymbol=not back)
  result.update(id=r['id'],block_size=k,backsymbol=back)
  if result['status'] in ('halt','infinite'):
   with lock:solved.add(r['id'])
  return result
 out={'settings':{'timeout':6,'max_loops':50000,'workers':2},'results':[]}
 with ThreadPoolExecutor(max_workers=2) as pool:
  fs=[pool.submit(work,j) for j in jobs]
  for f in as_completed(fs):
   r=f.result();out['results'].append(r);out['elapsed_seconds']=time.monotonic()-start
   Path('candidate_portfolio.json').write_text(json.dumps(out,indent=2))
   print(json.dumps({k:r[k] for k in ('id','status','block_size')}),flush=True)
