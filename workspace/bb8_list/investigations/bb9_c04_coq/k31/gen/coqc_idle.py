"""Compile one .v against busycoq + ../lib (BB8) + ../dev (Dev, read-only) + ../k31 (K31) at Idle priority.
Records the coqc PID in k31/pids.txt.  python coqc_idle.py FILE.v [TIMEOUT]   (k31 copy of gen/coqc_idle.py)"""
import subprocess, sys, time
from pathlib import Path
K = Path(__file__).resolve().parents[1]          # bb9_c04_coq/k31
W = K.parent                                     # bb9_c04_coq
BUSY = (W / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(W / 'lib'), 'BB8', '-Q', str(W / 'dev'), 'Dev', '-Q', str(K), 'K31']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(K / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v, time.strftime('%Y-%m-%d %H:%M:%S')))
try:
    out, _ = p.communicate(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 7200)
except subprocess.TimeoutExpired:
    p.kill(); out, _ = p.communicate()
    print('TIMEOUT')
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (out or '').strip()
print(out[-6000:])
