import idle
"""Compile one .v of the X tree (bb9_f3_coq/x) at Idle priority.  python cq.py FILE.v [TIMEOUT_S]
Logical paths: busycoq = BusyCoq, x/lib = XL, x/dev = XDev, x/k31 = XK31, x/score = XScore, x/fgh = XFgh,
c7/ = C7 (the 9-state layer), and ext/tree/lib (C04's lib: BB92/Individual92 + fw2 files, compiled) = BB8.
With CMP=1 also ext/tree's C04 and M8 trees (Dev, K31, Score, Fgh, M8, BB8 = bb8v too).
Records the coqc PID in bb9_f3_coq/pids.txt; writes logs/<name>.log and logs/<name>.done (exit code + seconds)."""
import subprocess, sys, time, os
from pathlib import Path
W = Path(__file__).resolve().parents[1]
F3 = W.parent / 'bb9_f3_coq'
BUSY = F3 / 'ext' / 'busycoq' / 'verify'          # busycoq bd2e36f, the build used by ext/tree (verify_easy's)
COQC = os.path.join('C:' + os.sep, 'Coq-Platform~8.20~2025.01', 'bin', 'coqc.exe')
X = W / 'x'
T = F3 / 'ext' / 'tree'                              # compiled C04 + M8 tree (verify_easy's split build of 78bd08e)
FLAGS = ['-Q', str(BUSY), 'BusyCoq', '-Q', str(X / 'lib'), 'XL', '-Q', str(X / 'dev'), 'XDev', '-Q', str(X / 'k31'), 'XK31',
         '-Q', str(X / 'score'), 'XScore', '-Q', str(X / 'fgh'), 'XFgh', '-Q', str(W / 'c7'), 'C7', '-Q', str(T / 'lib'), 'BB8']
if os.environ.get('CMP'):                           # the comparison with M8 also loads the C04 and M8 trees
    FLAGS += ['-Q', str(T / 'bb8v'), 'BB8', '-Q', str(T / 'dev'), 'Dev', '-Q', str(T / 'k31'), 'K31', '-Q', str(T / 'score'),
              'Score', '-Q', str(T / 'fgh'), 'Fgh', '-Q', str(T / 'm8'), 'M8']
v = Path(sys.argv[1]).resolve()
name = v.parent.name + '_' + v.stem
log = W / 'logs' / (name + '.log'); done = W / 'logs' / (name + '.done')
if done.exists(): done.unlink()
t0 = time.time()
with open(log, 'w') as lf:
    p = subprocess.Popen([COQC] + FLAGS + [v.name], cwd=v.parent, stdout=lf, stderr=subprocess.STDOUT,
                         creationflags=subprocess.IDLE_PRIORITY_CLASS)
    with open(W / 'pids.txt', 'a') as f:
        f.write('%d coqc %s %s\n' % (p.pid, v, time.strftime('%Y-%m-%d %H:%M:%S')))
    try:
        rc = p.wait(timeout=int(sys.argv[2]) if len(sys.argv) > 2 else 20000)
    except subprocess.TimeoutExpired:
        p.kill(); rc = 'TIMEOUT'
done.write_text('exit %s %.1fs\n' % (rc, time.time() - t0))
print(name, 'exit', rc, '%.1fs' % (time.time() - t0))
