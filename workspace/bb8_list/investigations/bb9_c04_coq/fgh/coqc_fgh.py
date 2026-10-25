"""Compile one fgh/*.v at Idle priority.  python coqc_fgh.py FILE.v [TIMEOUT] [MAXGB]
Load path: busycoq (BusyCoq), bb8_list/proofs (BB8; Individual92.vo/BB92.vo byte-identical to ../lib), dev (Dev),
k31 (K31), score (Score) -- all read-only -- and fgh (Fgh).  Records the coqc PID in fgh/pids.txt."""
import subprocess, sys, time
from pathlib import Path
F = Path(__file__).resolve().parent          # bb9_c04_coq/fgh
W = F.parent                                 # bb9_c04_coq
BUSY = (W / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
PROOFS = (W / '..' / '..' / 'proofs').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(W / 'dev'), 'Dev',
         '-Q', str(W / 'k31'), 'K31', '-Q', str(W / 'score'), 'Score', '-Q', str(F), 'Fgh']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(F / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v.name, time.strftime('%Y-%m-%d %H:%M:%S')))
import threading
MAXKB = int(sys.argv[3]) * 1024 * 1024 if len(sys.argv) > 3 else 6 * 1024 * 1024   # memory cap (GB arg), default 6 GB
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
    out, _ = p.communicate(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 3600)
except subprocess.TimeoutExpired:
    p.kill(); out, _ = p.communicate()
    print('TIMEOUT')
if killed:
    print('KILLED: memory %d KB over cap' % killed[0])
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (out or '').strip()
print(out[-8000:])
