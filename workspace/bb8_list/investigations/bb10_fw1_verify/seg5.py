"""Seg5: the second unpack event in the real classes: [6^(4B+1),3,A1-8,A''+1,0,1^(8B+55) | A'''] -> HALT,
fixed 20-token tail, ones = 7n + Y + 3T/2 + 9w/5 + 3A/5 + 131/10.   seg5.py MOD NPROC spec..."""
import sys, os, subprocess
from fractions import Fraction as F
from fw import *
from res import A_deep, B_rec
MOD = int(sys.argv[1]); nproc = int(sys.argv[2])
ad = A_deep(MOD); br = B_rec(MOD)
jobs = []
for spec in sys.argv[3:]:
    bk, k1, k3, kpp = map(int, spec.split(','))    # B = br + bk*MOD, A1 = ad + k1*MOD, A''' = ad + k3*MOD, A'' = ad + kpp*MOD
    B = br + bk * MOD; A1 = ad + k1 * MOD; A3 = ad + k3 * MOD; App = ad + kpp * MOD
    n = 4 * B + 1; Y = A1 - 8; T = App + 1; w = 8 * B + 55
    L = [6] * n + [3, Y, T, 0] + [1] * w
    wd, h, q = bword(L, A3)
    jobs.append(('B%d_A1%d_A3%d_App%d' % (B, A1, A3, App), wd, h, q, (n, Y, T, w, A3)))
parts = [jobs[i::nproc] for i in range(nproc)]
procs = []
for i, p in enumerate(parts):
    fn = os.path.join(HERE, 'tmp', 'seg5_%d_%d.txt' % (MOD, i))
    with open(fn, 'w') as f:
        for lab, wd, h, q, _ in p:
            f.write('%s %s %d %s\n' % (lab, wd, h, q))
    procs.append(subprocess.Popen([SIM, M10, fn, str(10 ** 13), 'Bf', '1'], stdout=open(fn + '.out', 'w'), creationflags=IDLE))
for pr in procs:
    pr.wait()
par = {lab: v for lab, _, _, _, v in jobs}
TAIL = [1, 0, 'z2', 0, 0, 'z2', 0, 0, 0, 0, 'z2', 0, 'z2', 0, 0, 0, 'z2', 0, 'z2', 1]
for i in range(nproc):
    for line in open(os.path.join(HERE, 'tmp', 'seg5_%d_%d.txt.out' % (MOD, i))):
        x = parse(line)
        if x['kind'] == 'END' or x['kind'] == '?':
            continue
        n, Y, T, w, A = par[x['lab']]
        if x['kind'] == 'HALT':
            it, idx, off = tokpos(x['word'], x['rel'])
            pred = 7 * n + Y + F(3, 2) * T + F(9, 5) * w + F(3, 5) * A + F(131, 10)
            print(x['lab'], 'HALT step=%d' % x['step'], 'tail20=%s' % (it[idx:] == TAIL), 'prefix_intact=%s' % (it[:n + 2] == [6] * n + [3, Y]),
                  'ones=%d formula=%s %s' % (x['ones'], pred, 'OK' if pred == x['ones'] else 'DIFF'), flush=True)
        else:
            print(x['lab'], x['kind'], flush=True)
