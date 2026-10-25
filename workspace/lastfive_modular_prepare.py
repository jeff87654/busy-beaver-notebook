from pathlib import Path
import subprocess,os,json,hashlib
root=Path(__file__).resolve().parent
env=os.environ.copy();env['PATH']=r'C:\msys64\ucrt64\bin;'+env['PATH']
cmd=[r'C:\msys64\ucrt64\bin\g++.exe','-O0','-std=c++17','lastfive_modular_unit.cpp','-o','lastfive_modular_unit.exe']
p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=120)
Path('lastfive_modular_unit_build.log').write_text(p.stdout+p.stderr)
assert p.returncode==0,p.stderr
p=subprocess.run([str(root/'lastfive_modular_unit.exe')],env=env,capture_output=True,text=True,timeout=10)
Path('lastfive_modular_unit.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
base=Path('unresolved_native_exrwl.py').read_text();a=base.index('PORTFOLIO=');b=base.index('\n\nPROVEN=',a)
commands=[f'MitM_CTL Modular sim 1001 maxT 300000 m {m} k {k} lmod 1 n {n} run' for k in (2,4,6,8) for n in (1,2,3) for m in (3,5,7,9,15,31)]
base=base[:a]+'PORTFOLIO='+repr(commands)+base[b:]
base=base.replace('candidate_deciders_deep_verified.exe','lastfive_modular_native.exe').replace('unresolved_native_exrwl_runs','lastfive_modular_runs').replace('unresolved_native_exrwl.json','lastfive_modular_results.json').replace('{3,5,6,13,15}','{13,15}').replace('deadline=start+180','deadline=start+60').replace('min(8,max','min(3,max')
base=base.replace("'capacity_change':'Word capacity increased from 128 to 256 bits to support requested 32/48-item state-annotated histories.'","'custom_abstraction':'Full binary-stack residue plus exact near-head suffix; character history disabled. Entire source verifier unchanged.'")
base=base.replace("(ROOT/'candidate_deciders_deep_verified.cpp')","(ROOT/'lastfive_modular_native.cpp')")
Path('lastfive_modular_portfolio.py').write_text(base)
# Positive control: forever move right while writing1; negative control: halt immediately.
controls=[]
for name,machine,want in [('loop','_'.join(['1RA1RA']*8),True),('halt','_'.join(['---1RA']+['1RA1RA']*7),False)]:
 d=root/'lastfive_modular_runs'/('calibration_'+name);d.mkdir(parents=True,exist_ok=True)
 (d/'input.txt').write_text(machine+' MitM_CTL Modular maxT 10000 m 3 k 4 lmod 1 n 2 run\n')
 p=subprocess.run([str(root/'lastfive_modular_native.exe'),'exec','input.txt'],cwd=d,env=env,capture_output=True,text=True,timeout=5)
 (d/'stdout.txt').write_text(p.stdout);(d/'stderr.txt').write_text(p.stderr)
 log=(d/'log.txt').read_text();proved=machine+' N' in log
 assert p.returncode==0 and proved==want,(name,p.returncode,p.stderr,log)
 if want:assert 'verified:' in p.stderr
 controls.append({'name':name,'machine':machine,'proved_nonhalting':proved,'stderr':p.stderr,'log':log})
Path('lastfive_modular_calibration.json').write_text(json.dumps({'unit_result':Path('lastfive_modular_unit.log').read_text(),'controls':controls},indent=2))
print('CALIBRATION PASSED',flush=True)
p=subprocess.run([os.sys.executable,'lastfive_modular_portfolio.py'],env=env,timeout=90)
raise SystemExit(p.returncode)
