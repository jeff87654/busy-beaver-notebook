"""Compile one .v of verify_easy/ against the existing (read-only) C04 / M8 development, at Idle priority.
   python coqc_ve.py FILE.v [TIMEOUT_S] [MAXGB]
Load path as in bb9_c04_coq/fgh/coqc_fgh.py: BusyCoq = third_party/busycoq/verify, BB8 = bb8_list/proofs,
Dev/K31/Score/Fgh = bb9_c04_coq/{dev,k31,score,fgh}, M8 = bb8_resid/coq_m8, Main = verify_easy/pkg/main.
Records the coqc PID in verify_easy/pids.txt; kills only that PID (memory cap / timeout)."""
import subprocess, sys, time, threading, os
from pathlib import Path
VE = Path(__file__).resolve().parent.parent
INV = VE.parent
W = INV / 'bb9_c04_coq'
BUSY = (INV / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
PROOFS = (INV / '..' / 'proofs').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(W / 'dev'), 'Dev',
         '-Q', str(W / 'k31'), 'K31', '-Q', str(W / 'score'), 'Score', '-Q', str(W / 'fgh'), 'Fgh',
         '-Q', str(INV / 'bb8_resid' / 'coq_m8'), 'M8', '-Q', str(VE / 'pkg' / 'main'), 'Main']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + os.environ.get('COQC_EXTRA', '').split() + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(VE / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v.name, time.strftime('%Y-%m-%d %H:%M:%S')))
MAXKB = int(sys.argv[3]) * 1024 * 1024 if len(sys.argv) > 3 else 4 * 1024 * 1024
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
lim = int(os.environ.get('OUT_TAIL', '8000'))
print(out[-lim:])
