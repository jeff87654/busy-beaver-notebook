"""(fgh copy for Headline8.v) Compile one .v with coq_m8's load path at Idle priority.  python coqc_m8.py FILE.v [TIMEOUT] [MAXGB]
Load path: busycoq (BusyCoq), ../coq_m8_devlib (BB8 = the C04 tree's lib/), the C04 development bb9_c04_coq: dev (Dev), k31 (K31),
score (Score), fgh (Fgh) -- all read-only, never recompiled -- and coq_m8 (M8).  Records the coqc PID in coq_m8/pids.txt.
(Adapted from bb9_c04_coq/fgh/coqc_fgh.py.)"""
import subprocess, sys, time, threading
from pathlib import Path
F = Path(__file__).resolve().parent                    # bb9_c04_coq/fgh
M = (F / '..' / '..' / 'bb8_resid' / 'coq_m8').resolve()   # coq_m8 (read-only)
W = (M / '..' / '..' / 'bb9_c04_coq').resolve()        # C04 development (read-only)
BUSY = (M / '..' / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
# BB8 = the C04 tree's lib/ (BB92, Individual92, BB9_fw2_1RB0RD, BB9_fw2_bound): byte-identical copies of the bb8_list/proofs
# 
# .v/.vo in ../coq_m8_devlib (outside this folder: -Q M8 is recursive), so nothing else from bb8_list/proofs can be loaded by accident.
PROOFS = M.parent / 'coq_m8_devlib'
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(W / 'dev'), 'Dev',
         '-Q', str(W / 'k31'), 'K31', '-Q', str(W / 'score'), 'Score', '-Q', str(W / 'fgh'), 'Fgh', '-Q', str(M), 'M8']
v = Path(sys.argv[1]).resolve()
# Beats8.v (optional comparison with the BB(8) champion) and probe.v also load the repo's BB8/verify files (logical BB8):
# byte-identical copies of the bb8_list/proofs BB82, Individual82, BB8_champ35_{1RB0RA,bound,exact} .v/.vo in ../coq_m8_devlib8.
if v.name in ('Beats8.v', 'probe.v'):
    FLAGS = FLAGS + ['-Q', str(M.parent / 'coq_m8_devlib8'), 'BB8']
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(F / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v.name, time.strftime('%Y-%m-%d %H:%M:%S')))
MAXKB = int(sys.argv[3]) * 1024 * 1024 if len(sys.argv) > 3 else 4 * 1024 * 1024   # memory cap (GB arg), default 4 GB
killed = []
def watch():
    while p.poll() is None:
        try:
            o = subprocess.run(['tasklist', '/FI', 'PID eq %d' % p.pid, '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
            kb = int(o.strip().split('","')[-1].replace('"', '').replace(',', '').replace(' K', '').strip() or 0)
            if kb > MAXKB:
                killed.append(kb); p.kill(); return
        except Exception:
            pass
        time.sleep(2)
threading.Thread(target=watch, daemon=True).start()
try:
    out, _ = p.communicate(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 1800)
except subprocess.TimeoutExpired:
    p.kill(); out, _ = p.communicate()
    print('TIMEOUT')
if killed:
    print('KILLED: memory %d KB over cap' % killed[0])
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (out or '').strip()
print(out[-8000:])
