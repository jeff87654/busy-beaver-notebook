"""Queue of cq.py compiles, launching only while fewer than CAP of MY coqc processes (PIDs in pids.txt) are alive.
python runq2.py CAP QUEUEFILE.  Log: logs/runq_<queue>.txt."""
import subprocess, sys, time, os
from pathlib import Path
W = Path(__file__).resolve().parents[1]
CAP = int(sys.argv[1]); q = [l.strip() for l in open(sys.argv[2]) if l.strip() and not l.startswith('#')]
out = open(W / 'logs' / ('runq_' + Path(sys.argv[2]).stem + '.txt'), 'a')
with open(W / 'pids.txt', 'a') as f:
    f.write('%d runq2 %s %s\n' % (os.getpid(), sys.argv[2], time.strftime('%Y-%m-%d %H:%M:%S')))
def alive():
    pids = [int(l.split()[0]) for l in open(W / 'pids.txt') if ' coqc ' in l]
    tl = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq coqc.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    live = {int(x.split('","')[1]) for x in tl.strip().splitlines() if x.startswith('"coqc')}
    return len([p for p in pids if p in live])
run = []
while q or run:
    if q and alive() < CAP:
        v = q.pop(0)
        run.append((v, subprocess.Popen([sys.executable, str(W / 'tools' / 'cq.py'), v], stdout=subprocess.PIPE, text=True)))
        out.write('%s start %s\n' % (time.strftime('%H:%M:%S'), v)); out.flush()
        time.sleep(10); continue
    time.sleep(20)
    for v, p in run[:]:
        if p.poll() is not None:
            out.write('%s %s' % (time.strftime('%H:%M:%S'), p.stdout.read())); out.flush()
            run.remove((v, p))
out.write('%s QUEUE DONE\n' % time.strftime('%H:%M:%S')); out.close()
