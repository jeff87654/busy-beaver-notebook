"""Compile one score/ .v at Idle priority.  python coqc_score.py FILE.v [TIMEOUT] [--fw2]
Load path: busycoq (BusyCoq), ../lib (BB8), ../dev (Dev), . (Score).  With --fw2, BB8 is bb8_list/proofs instead of ../lib
(the Individual92.vo / BB92.vo there are byte-identical to ../lib's, and proofs/ holds the compiled BB9_fw2_bound.vo).
Records the coqc PID in score/pids.txt."""
import subprocess, sys, time
from pathlib import Path
S = Path(__file__).resolve().parent
W = S.parent
BUSY = (W / '..' / '..' / '..' / 'third_party' / 'busycoq' / 'verify').resolve()
PROOFS = (W / '..' / '..' / 'proofs').resolve()
COQC = r'C:\Coq-Platform~8.20~2025.01\bin\coqc.exe'
args = [a for a in sys.argv[1:] if not a.startswith('--')]
bb8 = PROOFS if '--fw2' in sys.argv else W / 'lib'
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(bb8), 'BB8', '-Q', str(W / 'dev'), 'Dev', '-Q', str(S), 'Score']
v = Path(args[0]).resolve()
t0 = time.time()
p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, creationflags=subprocess.IDLE_PRIORITY_CLASS)
with open(S / 'pids.txt', 'a') as f:
    f.write('%d coqc %s %s\n' % (p.pid, v.name, time.strftime('%Y-%m-%d %H:%M:%S')))
try:
    out, _ = p.communicate(timeout=int(args[1]) if len(args) > 1 else 3600)
except subprocess.TimeoutExpired:
    p.kill(); out, _ = p.communicate()
    print('TIMEOUT')
print('exit', p.returncode, '%.1fs' % (time.time() - t0))
out = (out or '').strip()
print(out[-6000:])
