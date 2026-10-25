"""Bounded CTL-closure proof portfolio, using upstream's verifier-enabled exec path."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib,json,os,subprocess,time

ROOT=Path(__file__).resolve().parent
EXE=ROOT/'lastfive_modular_native.exe'
RUNS=ROOT/'lastfive_modular_odd_runs';RUNS.mkdir(exist_ok=True)
MACHINES=(ROOT/'discovery_holdouts.txt').read_text().splitlines()
ORIGINS={r['machine']:{k:r[k] for k in ('origin_file','origin_line','original_partial_machine') if k in r}
         for r in json.loads((ROOT/'discovery_final.json').read_text())['results']}
PORTFOLIO=['MitM_CTL Modular sim 1001 maxT 300000 m 3 k 3 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 3 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 3 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 3 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 3 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 3 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 3 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 3 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 3 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 3 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 3 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 3 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 3 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 3 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 3 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 3 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 3 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 3 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 5 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 5 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 5 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 5 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 5 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 5 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 5 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 5 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 5 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 5 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 5 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 5 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 5 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 5 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 5 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 5 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 5 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 5 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 7 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 7 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 7 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 7 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 7 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 7 lmod 1 n 1 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 7 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 7 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 7 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 7 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 7 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 7 lmod 1 n 2 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 3 k 7 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 5 k 7 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 7 k 7 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 9 k 7 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 15 k 7 lmod 1 n 3 run', 'MitM_CTL Modular sim 1001 maxT 300000 m 31 k 7 lmod 1 n 3 run']

PROVEN={r['id'] for r in json.loads((ROOT/'candidate_deciders.json').read_text())['results'] if r['status']=='verified_nonhalting_replayed'}

env=os.environ.copy();env['PATH']=r'C:\msys64\ucrt64\bin;'+env.get('PATH','')
for key in list(env):
 if key.startswith('BB_PILOT_'):env.pop(key)
start=time.monotonic();deadline=start+30
data={'engine':'mxdys MitM_CTL using verifier-enabled exec mode',
      'source':'https://github.com/ccz181078/TM',
      'executable_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),
      'upstream_source_sha256':hashlib.sha256((ROOT/'mxdys_main.cpp').read_bytes()).hexdigest(),
      'custom_abstraction':'Full binary-stack residue plus exact near-head suffix; character history disabled. Entire source verifier unchanged.',
      'diagnostic_source_sha256':hashlib.sha256((ROOT/'lastfive_modular_native.cpp').read_bytes()).hexdigest(),
      'verification':'Each successful closure passes CTL_Fixedlen_verify::Verifier because exec does not set CTL_skip_verify. Successful commands are replayed in a fresh process.',
      'portfolio':PORTFOLIO,'results':[{'id':i+1,'machine':m,'origin':ORIGINS.get(m,{}),'status':('unresolved' if i+1 in {13,15} else 'not_targeted'),'attempts':[]} for i,m in enumerate(MACHINES)]}

def save():
 data['elapsed_seconds']=time.monotonic()-start
 (ROOT/'lastfive_modular_odd_results.json').write_text(json.dumps(data,indent=2))

def attempt(i,p,replay=False):
 m=MACHINES[i];cmd=PORTFOLIO[p]
 d=RUNS/f'c{i+1:02d}_p{p:02d}{"_replay" if replay else ""}';d.mkdir(exist_ok=True)
 encoded=m.replace('1RZ','---');line=encoded+' '+cmd+'\n'
 (d/'input.txt').write_text(line)
 t=time.monotonic()
 r={'portfolio_index':p,'command':cmd,'input_file':str(d/'input.txt'),'replay':replay}
 try:
  completed=subprocess.run([str(EXE),'exec','input.txt'],cwd=d,env=env,capture_output=True,text=True,timeout=min(3,max(0.05,deadline-time.monotonic())))
  r['returncode']=completed.returncode
  (d/'stdout.txt').write_text(completed.stdout);(d/'stderr.txt').write_text(completed.stderr)
  log=(d/'log.txt').read_text() if (d/'log.txt').exists() else ''
  r['log']=log
  r['verifier_diagnostics']=completed.stderr if 'verified:' in completed.stderr else None
  if 'unknown cmd:' in completed.stderr:r['status']='unsupported'
  elif completed.returncode!=0:r['status']='error'
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
