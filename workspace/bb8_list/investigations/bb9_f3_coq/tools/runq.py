"""Run a queue of cq.py compiles, at most N at a time.  python runq.py N QUEUEFILE   (one .v path per line, in order).
Writes logs/runq_<queue>.txt.  Each coqc PID is recorded in pids.txt by cq.py."""
import subprocess, sys, time, os
from pathlib import Path
W = Path(__file__).resolve().parents[1]
N = int(sys.argv[1]); q = [l.strip() for l in open(sys.argv[2]) if l.strip() and not l.startswith('#')]
out = open(W / 'logs' / ('runq_' + Path(sys.argv[2]).stem + '.txt'), 'a')
with open(W / 'pids.txt', 'a') as f:
    f.write('%d runq %s %s\n' % (os.getpid(), sys.argv[2], time.strftime('%Y-%m-%d %H:%M:%S')))
run = []
while q or run:
    while q and len(run) < N:
        v = q.pop(0)
        run.append((v, subprocess.Popen([sys.executable, str(W / 'tools' / 'cq.py'), v], stdout=subprocess.PIPE, text=True)))
        out.write('%s start %s\n' % (time.strftime('%H:%M:%S'), v)); out.flush()
    time.sleep(5)
    for v, p in run[:]:
        if p.poll() is not None:
            out.write('%s %s' % (time.strftime('%H:%M:%S'), p.stdout.read())); out.flush()
            run.remove((v, p))
out.write('%s QUEUE DONE\n' % time.strftime('%H:%M:%S')); out.close()
