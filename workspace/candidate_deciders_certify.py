from pathlib import Path
import hashlib,json,os,re,subprocess,time
root=Path(__file__).resolve().parent
exe=root/'candidate_deciders_verified.exe'
data=json.loads((root/'candidate_deciders.json').read_text())
env=os.environ.copy();env['PATH']=r'C:\msys64\ucrt64\bin;'+env.get('PATH','')
for k in list(env):
 if k.startswith('BB_PILOT_'):env.pop(k)
t0=time.monotonic()
for result in data['results']:
 if result['status']!='verified_nonhalting_replayed':continue
 prior=next(a for a in reversed(result['attempts']) if a['status']=='verified_nonhalting')
 work=root/'candidate_deciders_runs'/('c%02d_verified'%result['id']);work.mkdir(exist_ok=True)
 tm=result['machine'].replace('1RZ','---')
 (work/'input.txt').write_text(tm+' '+prior['command']+'\n')
 done=subprocess.run([str(exe),'verify','input.txt'],cwd=work,env=env,capture_output=True,text=True,timeout=30)
 (work/'stdout.txt').write_text(done.stdout);(work/'stderr.txt').write_text(done.stderr)
 log=(work/'log.txt').read_text()
 match=re.search(r'verified: lset:(\d+) lset_tr:(\d+) rset:(\d+) rset_tr:(\d+) accept_set:(\d+) block_maxT:(\d+)',done.stderr)
 assert done.returncode==0 and tm+' N' in log and match,(result['id'],done.returncode,done.stderr)
 diag=dict(zip(['left_dfa_states','left_dfa_transitions','right_dfa_states','right_dfa_transitions','accepted_abstract_configurations','maximum_steps_in_verified_block'],map(int,match.groups())))
 diag.update(command=prior['command'],input_file=str(work/'input.txt'),stderr_file=str(work/'stderr.txt'),proof_certificate_exported=False)
 result['verifier_diagnostics']=diag
 print('C%02d'%result['id'],diag,flush=True)
data['diagnostic_build']={'source':'candidate_deciders_verified.cpp','source_sha256':hashlib.sha256((root/'candidate_deciders_verified.cpp').read_bytes()).hexdigest(),'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'change':'Enable existing verifier success diagnostics only; proof search and verification logic unchanged.','build_command':r'C:\msys64\ucrt64\bin\g++.exe candidate_deciders_verified.cpp -O2 -std=c++17 -DBB_STATES=8 -o candidate_deciders_verified.exe','elapsed_replay_seconds':time.monotonic()-t0}
(root/'candidate_deciders.json').write_text(json.dumps(data,indent=2))
