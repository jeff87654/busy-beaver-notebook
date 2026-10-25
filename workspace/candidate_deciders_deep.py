"""Bounded CTL-closure proof portfolio, using upstream's verifier-enabled exec path."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib,json,os,subprocess,time

ROOT=Path(__file__).resolve().parent
EXE=ROOT/'candidate_deciders_deep_verified.exe'
RUNS=ROOT/'candidate_deciders_deep_runs';RUNS.mkdir(exist_ok=True)
MACHINES=(ROOT/'discovery_holdouts.txt').read_text().splitlines()
ORIGINS={r['machine']:{k:r[k] for k in ('origin_file','origin_line','original_partial_machine') if k in r}
         for r in json.loads((ROOT/'discovery_final.json').read_text())['results']}
PORTFOLIO=[
 'chr_LRUH 32 chr_H 24 MitM_CTL NG maxT 300000 NG_n 4 run',
 'chr_LRUH 48 chr_H 32 MitM_CTL NG maxT 300000 NG_n 3 run',
 'MitM_CTL RWL_mod sim 1001 maxT 300000 H 8 mod 4 n 2 run',
 'MitM_CTL CPS_LRU sim 1001 maxT 300000 LRUH 16 H 2 tH 2 n 3 run',
]
PROVEN={r['id'] for r in json.loads((ROOT/'candidate_deciders.json').read_text())['results'] if r['status']=='verified_nonhalting_replayed'}

env=os.environ.copy();env['PATH']=r'C:\msys64\ucrt64\bin;'+env.get('PATH','')
for key in list(env):
 if key.startswith('BB_PILOT_'):env.pop(key)
start=time.monotonic();deadline=start+180
data={'engine':'mxdys MitM_CTL using verifier-enabled exec mode',
      'source':'https://github.com/ccz181078/TM',
      'executable_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),
      'upstream_source_sha256':hashlib.sha256((ROOT/'mxdys_main.cpp').read_bytes()).hexdigest(),
      'capacity_change':'Word capacity increased from 128 to 256 bits to support requested 32/48-item state-annotated histories.',
      'diagnostic_source_sha256':hashlib.sha256((ROOT/'candidate_deciders_deep_verified.cpp').read_bytes()).hexdigest(),
      'verification':'Each successful closure passes CTL_Fixedlen_verify::Verifier because exec does not set CTL_skip_verify. Successful commands are replayed in a fresh process.',
      'portfolio':PORTFOLIO,'results':[{'id':i+1,'machine':m,'origin':ORIGINS.get(m,{}),'status':('previously_verified_nonhalting' if i+1 in PROVEN else 'unresolved'),'attempts':[]} for i,m in enumerate(MACHINES)]}

def save():
 data['elapsed_seconds']=time.monotonic()-start
 (ROOT/'candidate_deciders_deep.json').write_text(json.dumps(data,indent=2))

def attempt(i,p,replay=False):
 m=MACHINES[i];cmd=PORTFOLIO[p]
 d=RUNS/f'c{i+1:02d}_p{p:02d}{"_replay" if replay else ""}';d.mkdir(exist_ok=True)
 encoded=m.replace('1RZ','---');line=encoded+' '+cmd+'\n'
 (d/'input.txt').write_text(line)
 t=time.monotonic()
 r={'portfolio_index':p,'command':cmd,'input_file':str(d/'input.txt'),'replay':replay}
 try:
  completed=subprocess.run([str(EXE),'exec','input.txt'],cwd=d,env=env,capture_output=True,text=True,timeout=min(8,max(0.05,deadline-time.monotonic())))
  r['returncode']=completed.returncode
  (d/'stdout.txt').write_text(completed.stdout);(d/'stderr.txt').write_text(completed.stderr)
  log=(d/'log.txt').read_text() if (d/'log.txt').exists() else ''
  r['log']=log
  r['verifier_diagnostics']=completed.stderr if 'verified:' in completed.stderr else None
  if completed.returncode!=0:r['status']='error'
  elif encoded+' N' in log:r['status']='verified_nonhalting'
  elif encoded+' H' in log:r['status']='halting'
  else:r['status']='unresolved'
 except subprocess.TimeoutExpired as ex:
  r['status']='process_timeout'
  (d/'stdout.txt').write_bytes(ex.stdout or b'');(d/'stderr.txt').write_bytes(ex.stderr or b'')
 r['elapsed_seconds']=time.monotonic()-t
 return i,r

with ThreadPoolExecutor(max_workers=2) as pool:
 for p in range(len(PORTFOLIO)):
  remaining=[i for i,r in enumerate(data['results']) if r['status']=='unresolved']
  if not remaining or time.monotonic()>deadline-1:break
  jobs=[pool.submit(attempt,i,p) for i in remaining]
  successes=[]
  for future in as_completed(jobs):
   i,r=future.result();data['results'][i]['attempts'].append(r)
   if r['status']=='verified_nonhalting':successes.append(i)
   if r['status']=='halting':data['results'][i]['status']='halting'
   save()
  for i in successes:
   _,r=attempt(i,p,True);data['results'][i]['attempts'].append(r)
   if r['status']=='verified_nonhalting':
    data['results'][i]['status']='verified_nonhalting_replayed'
    print('PROVED',i+1,MACHINES[i],'portfolio',p,flush=True)
   save()
  print('ROUND',p,'remaining',sum(r['status']=='unresolved' for r in data['results']),'elapsed',round(time.monotonic()-start,2),flush=True)
save()
