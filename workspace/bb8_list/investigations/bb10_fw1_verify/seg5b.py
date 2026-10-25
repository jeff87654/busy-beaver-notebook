"""Seg5 with explicit values (mod-6600 real class).  seg5b.py B,A1,A3,App ..."""
import sys, os, subprocess
from fractions import Fraction as F
from fw import *
jobs = []
for spec in sys.argv[1:]:
    B, A1, A3, App = map(int, spec.split(','))
    n = 4 * B + 1; Y = A1 - 8; T = App + 1; w = 8 * B + 55
    L = [6] * n + [3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A3)
    jobs.append(('B%d_A1%d_A3%d_App%d' % (B, A1, A3, App), wd, h, q, (n, Y, T, w, A3)))
procs = []
for i, (lab, wd, h, q, _) in enumerate(jobs):
    fn = os.path.join(HERE, 'tmp', 'seg5b_%d.txt' % i)
    open(fn, 'w').write('%s %s %d %s\n' % (lab, wd, h, q))
    procs.append(subprocess.Popen([SIM, M10, fn, str(10 ** 14), 'Bf', '1'], stdout=open(fn + '.out', 'w'), creationflags=IDLE))
for pr in procs:
    pr.wait()
TAIL = [1, 0, 'z2', 0, 0, 'z2', 0, 0, 0, 0, 'z2', 0, 'z2', 0, 0, 0, 'z2', 0, 'z2', 1]
for i, (lab, wd, h, q, (n, Y, T, w, A)) in enumerate(jobs):
    for line in open(os.path.join(HERE, 'tmp', 'seg5b_%d.txt.out' % i)):
        x = parse(line)
        if x['kind'] == 'HALT':
            it, idx, off = tokpos(x['word'], x['rel'])
            pred = 7 * n + Y + F(3, 2) * T + F(9, 5) * w + F(3, 5) * A + F(131, 10)
            print(lab, 'HALT step=%d' % x['step'], 'tail20=%s' % (it[idx:] == TAIL), 'prefix_intact=%s' % (it[:n + 2] == [6] * n + [3, Y]),
                  'ones=%d formula=%s %s' % (x['ones'], pred, 'OK' if pred == x['ones'] else 'DIFF'), flush=True)
        elif x['kind'] in ('BF', 'TIMEOUT'):
            print(lab, x['kind'], flush=True)
