"""like grid_ex.py but T = TF*A + TC (T = 1 mod 8) and reports pairs consumed (tokens right of halt) and C intact.
   grid_ex2.py OUT Alist wlist TF TC NPROC [Y]"""
import sys, os, subprocess, itertools
from fw import *
out = sys.argv[1]
As = eval(sys.argv[2]); ws = eval(sys.argv[3]); TF = int(sys.argv[4]); TC = int(sys.argv[5]); nproc = int(sys.argv[6])
Y = int(sys.argv[7]) if len(sys.argv) > 7 else 60
jobs = []
for A, w in itertools.product(As, ws):
    T = TF * A + TC
    T += (1 - T) % 8
    L = [6, 6, 3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    jobs.append(('A%d_w%d_Y%d_T%d' % (A, w, Y, T), wd, h, q))
parts = [jobs[i::nproc] for i in range(nproc)]
procs = []
for i, p in enumerate(parts):
    fn = os.path.join(HERE, 'tmp', 'gx2_%s_%d.txt' % (os.path.basename(out), i))
    with open(fn, 'w') as f:
        for lab, wd, h, q in p:
            f.write('%s %s %d %s\n' % (lab, wd, h, q))
    procs.append(subprocess.Popen([SIM, M10, fn, str(2 * 10 ** 11), 'Bf', '1'], stdout=open(fn + '.out', 'w'),
                                  creationflags=IDLE))
for pr in procs:
    pr.wait()
with open(out, 'w') as fo:
    for i in range(nproc):
        fn = os.path.join(HERE, 'tmp', 'gx2_%s_%d.txt.out' % (os.path.basename(out), i))
        for line in open(fn):
            x = parse(line)
            if x['kind'] == 'HALT':
                it, idx, off = tokpos(x['word'], x['rel'])
                # pairs left: count leading (D1 D0) pairs after the D0^2 marker
                k = 5; pairs = 0
                while k + 1 < len(it) and it[k] == 1 and it[k + 1] == 0:
                    pairs += 1; k += 2
                T = int(x['lab'].split('_T')[1])
                fo.write('%s HALT %d tokidx=%d ntok=%d left=%s pairs_left=%d of %d\n' % (
                    x['lab'], x['step'], idx, len(it), fmt(it[:5]), pairs, (T - 5) // 2))
            elif x['kind'] == 'BF':
                p = bparse(x['word'], x['rel'])
                fo.write('%s BF %d [%s | %d]\n' % (x['lab'], x['step'], fmt(p[0])[:150], p[1]))
            elif x['kind'] == 'TIMEOUT':
                fo.write('%s TIMEOUT\n' % x['lab'])
print('done', len(jobs))
