"""Independent Ligocki CTL1-4 passes for the two C13-C16 representatives."""
import sys,json,time,subprocess,importlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=='child':
 sys.path[:0]=[str(ROOT/'third_party/ligocki/Code'),str(ROOT/'third_party/runtime_deps')]
 import IO
 job=json.loads(sys.argv[2]);module=importlib.import_module(job['module'])
 cases=job.get('cases') or [(b,o) for b in (1,2,3,4,6) for o in range(b)]
 for b,o in cases:
  tm=IO.get_tm(job['machine']);start=time.monotonic()
  try:
   ok,it=module.test_CTL(tm,cutoff=1000,block_size=b,offset=o,use_backsymbol=True,verbose=False)
   result={'id':job['id'],'module':job['module'],'block_size':b,'offset':o,'status':'nonhalting' if ok else 'inconclusive','iterations':it,'seconds':time.monotonic()-start}
  except Exception as e:result={'id':job['id'],'module':job['module'],'block_size':b,'offset':o,'status':'error','error':repr(e)}
  print('RESULT '+json.dumps(result),flush=True)
  if result['status']=='nonhalting':break
 sys.exit(0)
rows=[r for r in json.loads((ROOT/'candidate_manifest.json').read_text()) if r['id'] in ('C13','C15')]
jobs=[dict(r,module=m) for r in rows for m in ('CTL1','CTL2','CTL3','CTL4')]
start=time.monotonic();out={'engine':'unmodified Ligocki CTL1-4','settings':{'cutoff':1000,'blocks':[1,2,3,4,6],'all_offsets':True,'backsymbol':True,'seconds_per_job':20},'results':[],'processes':[]}
def work(job):
 try:
  r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'child',json.dumps(job)],capture_output=True,text=True,timeout=20,cwd=ROOT)
  return job,r.stdout,r.returncode,False,r.stderr
 except subprocess.TimeoutExpired as e:return job,(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else (e.stdout or ''),None,True,''
with ThreadPoolExecutor(max_workers=2) as pool:
 for job,stdout,code,timeout,stderr in pool.map(work,jobs):
  results=[json.loads(line[7:]) for line in stdout.splitlines() if line.startswith('RESULT ')]
  out['results']+=results;out['processes'].append({'id':job['id'],'module':job['module'],'returncode':code,'timeout':timeout,'stderr_tail':stderr[-2000:]})
  out['elapsed_seconds']=time.monotonic()-start
  (ROOT/'unresolved_ligocki_ctl.json').write_text(json.dumps(out,indent=2))
  print(job['id'],job['module'],len(results),'positive',sum(r['status']=='nonhalting' for r in results),'timeout',timeout,flush=True)
