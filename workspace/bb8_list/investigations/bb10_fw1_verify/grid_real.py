"""real-class grid for the second unpack event: [6^n,3,Y,T,0,1^w | A] with A = A_deep, Y = A_deep-8,
T = A_deep+1, w = 8B+55 classes (mod 120), T >> A.  Reports outcome, steps, tokens right of the head at HALT,
whether the prefix [6^n,3,Y] is intact, and ones.   grid_real.py OUT NPROC"""
import sys, os, subprocess, itertools
from fw import *
out = sys.argv[1]; nproc = int(sys.argv[2])
jobs = []
for n, A, w, Y in itertools.product([1, 3], [40, 160, 280, 400, 520, 640], [103, 223, 343], [32, 152]):
    T = 40 * A + 401
    T += (41 - T) % 120
    L = [6] * n + [3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    jobs.append(('n%d_A%d_w%d_Y%d_T%d' % (n, A, w, Y, T), wd, h, q))
parts = [jobs[i::nproc] for i in range(nproc)]
procs = []
for i, p in enumerate(parts):
    fn = os.path.join(HERE, 'tmp', 'grl_%s_%d.txt' % (os.path.basename(out), i))
    with open(fn, 'w') as f:
        for lab, wd, h, q in p:
            f.write('%s %s %d %s\n' % (lab, wd, h, q))
    procs.append(subprocess.Popen([SIM, M10, fn, str(5 * 10 ** 11), 'Bf', '1'], stdout=open(fn + '.out', 'w'),
                                  creationflags=IDLE))
for pr in procs:
    pr.wait()
with open(out, 'w') as fo:
    for i in range(nproc):
        fn = os.path.join(HERE, 'tmp', 'grl_%s_%d.txt.out' % (os.path.basename(out), i))
        for line in open(fn):
            x = parse(line)
            if x['kind'] == 'HALT':
                it, idx, off = tokpos(x['word'], x['rel'])
                n = int(x['lab'].split('_')[0][1:]); Y = int(x['lab'].split('_Y')[1].split('_')[0])
                intact = it[:n + 2] == [6] * n + [3, Y]
                fo.write('%s HALT step=%d right=%d intact=%s ones=%d tail=%s\n' % (
                    x['lab'], x['step'], len(it) - idx, intact, x['ones'], fmt(it[idx:])[:120]))
            elif x['kind'] == 'BF':
                fo.write('%s BF\n' % x['lab'])
            elif x['kind'] == 'TIMEOUT':
                fo.write('%s TIMEOUT\n' % x['lab'])
print('done', len(jobs))
