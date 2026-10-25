"""No-residue-escape grid for configuration 13 in the real class mod 120 (B = 6 mod 120, deep values = 40 mod 120),
with every other residue (mod 7, 9, 11, 13, 25, ...) varied.  T = A''+1 only needs to exceed the pairs the cascade uses.
   noesc.py OUT NPROC"""
import sys, os, subprocess, random
from fractions import Fraction as F
from fw import *
out = sys.argv[1]; nproc = int(sys.argv[2])
rng = random.Random(2026)
TAIL = [1, 0, 'z2', 0, 0, 'z2', 0, 0, 0, 0, 'z2', 0, 'z2', 0, 0, 0, 'z2', 0, 'z2', 1]
jobs = []
for i in range(int(sys.argv[3])):
    B = 6 + 120 * rng.randint(0, 6); A3 = 40 + 120 * rng.randint(0, 29); A1 = 40 + 120 * rng.randint(0, 40)
    n = 4 * B + 1; Y = A1 - 8; w = 8 * B + 55
    T = 6 * A3 + 2 * w + 1001 + 120 * rng.randint(0, 20); T += (41 - T) % 120
    L = [6] * n + [3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A3)
    jobs.append(('j%d_B%d_A1%d_A3%d_T%d' % (i, B, A1, A3, T), wd, h, q, (n, Y, T, w, A3)))
parts = [jobs[i::nproc] for i in range(nproc)]
procs = []
for i, p in enumerate(parts):
    fn = os.path.join(HERE, 'tmp', 'noesc_%d.txt' % i)
    with open(fn, 'w') as f:
        for lab, wd, h, q, _ in p:
            f.write('%s %s %d %s\n' % (lab, wd, h, q))
    procs.append(subprocess.Popen([SIM, M10, fn, str(10 ** 13), 'Bf', '1'], stdout=open(fn + '.out', 'w'), creationflags=IDLE))
for pr in procs:
    pr.wait()
par = {lab: v for lab, _, _, _, v in jobs}
cnt = {}
with open(out, 'w') as fo:
    for i in range(nproc):
        for line in open(os.path.join(HERE, 'tmp', 'noesc_%d.txt.out' % i)):
            x = parse(line)
            if x['kind'] in ('END', '?'):
                continue
            n, Y, T, w, A = par[x['lab']]
            if x['kind'] == 'HALT':
                it, idx, off = tokpos(x['word'], x['rel'])
                pred = 7 * n + Y + F(3, 2) * T + F(9, 5) * w + F(3, 5) * A + F(131, 10)
                key = 'HALT tail=%s prefix=%s ones=%s' % (it[idx:] == TAIL, it[:n + 2] == [6] * n + [3, Y], pred == x['ones'])
                fo.write('%s %s step=%d ones=%d\n' % (x['lab'], key, x['step'], x['ones']))
            else:
                key = x['kind']
                fo.write('%s %s\n' % (x['lab'], key))
            cnt[key] = cnt.get(key, 0) + 1
print(cnt)
