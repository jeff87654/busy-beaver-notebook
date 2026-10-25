"""Compile one .v against busycoq (read-only build) + ../lib (logical BB8) + ../dev (logical Dev) at Idle priority.
Records the coqc PID in ../pids.txt.  python coqc_idle.py FILE.v [TIMEOUT]"""
import subprocess, sys, time
from pathlib import Path
W = Path(__file__).resolve().parents[1]
BUSY = (W / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(W / 'lib'), 'BB8', '-Q', str(W / 'dev'), 'Dev']
v = Path(sys.argv[1]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(W / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v.name, time.strftime('%Y-%m-%d %H:%M:%S')))
try:
    out, _ = p.communicate(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 7200)
except subprocess.TimeoutExpired:
    p.kill(); out, _ = p.communicate()
    print('TIMEOUT')
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (out or '').strip()
print(out[-6000:])
