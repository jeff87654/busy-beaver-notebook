"""Bounded CTL-closure proof portfolio, using upstream's verifier-enabled exec path."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import hashlib,json,os,subprocess,time

ROOT=Path(__file__).resolve().parent
EXE=ROOT/'mxdys_pilot8.exe'
RUNS=ROOT/'candidate_deciders_runs';RUNS.mkdir(exist_ok=True)
MACHINES=(ROOT/'discovery_holdouts.txt').read_text().splitlines()
ORIGINS={r['machine']:{k:r[k] for k in ('origin_file','origin_line','original_partial_machine') if k in r}
         for r in json.loads((ROOT/'discovery_final.json').read_text())['results']}
PORTFOLIO=[
 'chr_asth 0 chr_LRUH 1 chr_H 1 MitM_CTL NG maxT 100000 NG_n 3 run',
 'chr_LRUH 24 chr_H 16 MitM_CTL NG maxT 30000 NG_n 3 run',
 'chr_LRUH 14 chr_H 2 MitM_CTL NG maxT 10000 NG_n 4 run',
 'chr_LRUH 2 chr_H 2 MitM_CTL NG maxT 30000 NG_n 5 run',
 'chr_asth 0 chr_LRUH 48 chr_H 48 MitM_CTL NG maxT 30000 NG_n 5 run',
 'MitM_CTL RWL_mod sim 1001 maxT 100000 H 4 mod 2 n 2 run',
 'MitM_CTL RWL_mod sim 1001 maxT 100000 H 6 mod 3 n 2 run',
 'MitM_CTL CPS_LRU sim 1001 maxT 100000 LRUH 4 H 1 tH 1 n 4 run',
 'MitM_CTL CPS_LRU sim 1001 maxT 100000 LRUH 8 H 2 tH 0 n 3 run',
 'chr_LRUH 0 chr_H 0 MitM_CTL NG maxT 100000 NG_n 6 run',
 'chr_LRUH 0 chr_H 0 MitM_CTL NG maxT 100000 NG_n 7 n 2 run',
 'chr_LRUH 0 chr_H 0 MitM_CTL NG maxT 100000 NG_n 4 n 3 run',
]
env=os.environ.copy();env['PATH']=r'C:\msys64\ucrt64\bin;'+env.get('PATH','')
for key in list(env):
 if key.startswith('BB_PILOT_'):env.pop(key)
start=time.monotonic();deadline=start+300
data={'engine':'mxdys MitM_CTL using verifier-enabled exec mode',
      'source':'https://github.com/ccz181078/TM',
      'executable_sha256':hashlib.sha256(EXE.read_bytes()).hexdigest(),
      'upstream_source_sha256':hashlib.sha256((ROOT/'mxdys_main.cpp').read_bytes()).hexdigest(),
      'verification':'Each successful closure passes CTL_Fixedlen_verify::Verifier because exec does not set CTL_skip_verify. Successful commands are replayed in a fresh process.',
      'portfolio':PORTFOLIO,'results':[{'id':i+1,'machine':m,'origin':ORIGINS.get(m,{}),'status':'unresolved','attempts':[]} for i,m in enumerate(MACHINES)]}

def save():
 data['elapsed_seconds']=time.monotonic()-start
 (ROOT/'candidate_deciders.json').write_text(json.dumps(data,indent=2))

def attempt(i,p,replay=False):
 m=MACHINES[i];cmd=PORTFOLIO[p]
 d=RUNS/f'c{i+1:02d}_p{p:02d}{"_replay" if replay else ""}';d.mkdir(exist_ok=True)
 encoded=m.replace('1RZ','---');line=encoded+' '+cmd+'\n'
 (d/'input.txt').write_text(line)
 t=time.monotonic()
 r={'portfolio_index':p,'command':cmd,'input_file':str(d/'input.txt'),'replay':replay}
 try:
  completed=subprocess.run([str(EXE),'exec','input.txt'],cwd=d,env=env,capture_output=True,text=True,timeout=min(20,max(0.05,deadline-time.monotonic())))
  r['returncode']=completed.returncode
  (d/'stdout.txt').write_text(completed.stdout);(d/'stderr.txt').write_text(completed.stderr)
  log=(d/'log.txt').read_text() if (d/'log.txt').exists() else ''
  r['log']=log
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
