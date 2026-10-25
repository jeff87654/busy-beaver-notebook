"""exhausted-transit grid: [6^2,3,Y,T,0,1^w | A], T >> 2A.  Outcome per job via sim.exe (stop at first B-form).
   grid_ex.py OUT Alist wlist Ylist Tmode NPROC"""
import sys, os, subprocess, itertools
from fw import *
out = sys.argv[1]
As = eval(sys.argv[2]); ws = eval(sys.argv[3]); Ys = eval(sys.argv[4]); Tmode = sys.argv[5]; nproc = int(sys.argv[6])
jobs = []
for A, w, Y in itertools.product(As, ws, Ys):
    if Tmode == 'big':
        T = 2 * (A + w) + 400
        T += (1 - T) % 8
    else:
        T = int(Tmode)
    L = [6, 6, 3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A)
    jobs.append(('A%d_w%d_Y%d_T%d' % (A, w, Y, T), wd, h, q))
parts = [jobs[i::nproc] for i in range(nproc)]
procs = []
for i, p in enumerate(parts):
    fn = os.path.join(HERE, 'tmp', 'gex_%s_%d.txt' % (os.path.basename(out), i))
    with open(fn, 'w') as f:
        for lab, wd, h, q in p:
            f.write('%s %s %d %s\n' % (lab, wd, h, q))
    procs.append(subprocess.Popen([SIM, M10, fn, str(5 * 10 ** 9), 'Bf', '1'], stdout=open(fn + '.out', 'w'),
                                  creationflags=IDLE))
for pr in procs:
    pr.wait()
with open(out, 'w') as fo:
    for i in range(nproc):
        fn = os.path.join(HERE, 'tmp', 'gex_%s_%d.txt.out' % (os.path.basename(out), i))
        for line in open(fn):
            x = parse(line)
            if x['kind'] == 'HALT':
                it, idx, off = tokpos(x['word'], x['rel'])
                fo.write('%s HALT %d tokidx=%d ntok=%d left=%s\n' % (x['lab'], x['step'], idx, len(it), fmt(it[:4])))
            elif x['kind'] == 'BF':
                p = bparse(x['word'], x['rel'])
                fo.write('%s BF %d [%s | %d]\n' % (x['lab'], x['step'], fmt(p[0])[:150], p[1]))
            elif x['kind'] == 'TIMEOUT':
                fo.write('%s TIMEOUT\n' % x['lab'])
print('done', len(jobs))
