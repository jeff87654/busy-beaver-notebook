"""Compile a final-assembly .v (dev/ScoreEnd.v, dev/probe.v) at Idle priority.  python coqc_final.py FILE.v [TIMEOUT]
Load path: busycoq (BusyCoq), bb8_list/proofs (BB8; Individual92.vo/BB92.vo byte-identical to ../lib, plus the fw2 files),
dev (Dev), k31 (K31), score (Score).  Records the coqc PID in ../pids.txt."""
import subprocess, sys, time
from pathlib import Path
W = Path(__file__).resolve().parents[1]
BUSY = (W / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
PROOFS = (W / '..' / '..' / 'proofs').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(PROOFS), 'BB8', '-Q', str(W / 'dev'), 'Dev',
         '-Q', str(W / 'k31'), 'K31', '-Q', str(W / 'score'), 'Score']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(W / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v.name, time.strftime('%Y-%m-%d %H:%M:%S')))
try:
    out, _ = p.communicate(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 3600)
except subprocess.TimeoutExpired:
    p.kill(); out, _ = p.communicate()
    print('TIMEOUT')
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (out or '').strip()
print(out[-6000:])
