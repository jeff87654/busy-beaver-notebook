"""Second, recursive-proof pass over the initial pilot's unresolved machines."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json,time
from pathlib import Path
from ligocki_runner import run_machine

if __name__ == '__main__':
 start=time.monotonic()
 old=json.loads(Path('discovery_triage.json').read_text())
 records=[r for r in old['results'] if r['status']=='cutoff']
 options=dict(timeout=15,max_loops=100000,recursive=True)
 output={'configuration':dict(workers=2,**options),'source_sha256':old['source_sha256'],'source_modified':False,'results':[]}
 with ThreadPoolExecutor(max_workers=2) as pool:
  futures={pool.submit(run_machine,r['machine'],**options):r for r in records}
  for future in as_completed(futures):
   prior=futures[future]
   result=future.result()
   for k in ('origin_file','origin_line','original_partial_machine','completion'):
    result[k]=prior[k]
   output['results'].append(result)
   output['elapsed_seconds']=time.monotonic()-start
   output['counts']={status:sum(r['status']==status for r in output['results']) for status in ('halt','infinite','cutoff','undefined','error')}
   Path('discovery_deep.json').write_text(json.dumps(output,indent=2))
   print(json.dumps({'completed':len(output['results']),'origin_line':result['origin_line'],'status':result['status'],'reason':result['reason']}),flush=True)
 print(json.dumps({'counts':output['counts'],'elapsed_seconds':output['elapsed_seconds']}),flush=True)
