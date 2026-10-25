"""Run a machine list from c_end(q, r) on a grid of small (q, r); one xsim call per grid point (Idle priority).
Usage: python grid.py MACHFILE OUTPREFIX MAXSTEPS q1,q2,.. r1,r2,..  -> OUTPREFIX_q_r.txt"""
import subprocess, sys, os
from cend import c_end
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)
TMP = os.path.join(os.environ.get('CLAUDE_JOB_DIR', '.'), 'tmp', 'rec9ext')
os.makedirs(TMP, exist_ok=True)
mf, pre, ms = sys.argv[1], sys.argv[2], sys.argv[3]
qs = [int(x) for x in sys.argv[4].split(',')]
rs = [int(x) for x in sys.argv[5].split(',')]
procs = []
for q in qs:
    for r in rs:
        t, h, s = c_end(q, r)
        cf = os.path.join(TMP, f'ce_{q}_{r}.txt')
        open(cf, 'w').write(f'{s} {h}\n{t}\n')
        out = open(f'{pre}_{q}_{r}.txt', 'w')
        procs.append(subprocess.Popen([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xsim.exe'), mf, cf, ms],
                                      stdout=out, creationflags=LOW))
        if len(procs) >= 4:
            procs.pop(0).wait()
for p in procs:
    p.wait()
