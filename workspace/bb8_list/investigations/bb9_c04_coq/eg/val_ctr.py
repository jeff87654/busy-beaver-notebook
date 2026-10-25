"""val_ctr.py SEED N: counter lemmas.  C3: Kx(..d,3,1^(k+1);1;3R+2;t) -> Kx(..d,0,6R+7,1^k;1;2;t).
   H0: Kx(..d,0,1^(k+1);1;3R+2;t) -> HALT1 with tape l 1 (10)^s 1 (10)^(d-1) [H> 1111 (10)^(6R+3) 0 (101)^(k+3) (11100100)^t 101"""
import random, sys, subprocess, os
sys.path.insert(0, '../tools')
from lit import *
from rawparse import expand
rnd = random.Random(int(sys.argv[1])); N = int(sys.argv[2])
def far(): return '11' + ''.join(tok(rnd.randint(2, 40)) for _ in range(rnd.randint(1, 4)))[:-1]
def kx(l, toks, k, m, r, t): return l + '1' + ''.join('10' * d + '1' for d in toks) + '101' * k + '10' * m + '1' + '10' * r + '11' + T(t) + '1001'
bad = 0
for _ in range(N):
    l = far(); s = rnd.randint(0, 20); d = rnd.randint(1, 40); k = rnd.randint(0, 40); R = rnd.randint(0, 12); t = rnd.randint(0, 8)
    ok, out = check(kx(l, [s, d, 3], k + 1, 1, 3 * R + 2, t), kx(l, [s, d, 0, 6 * R + 7], k, 1, 2, t))
    if not ok: bad += 1; print('C3 FAIL', dict(s=s, d=d, k=k, R=R, t=t), out[:80])
    fs = os.path.join(TMP, 'h.txt'); open(fs, 'w').write(kx(l, [s, d, 0], k + 1, 1, 3 * R + 2, t))
    o = subprocess.run([EXE, '@file:%s:B' % fs, '--steps', '1e9'], capture_output=True, text=True).stdout.strip().split('\n')[-1]
    left, right = o.split(' ', 2)[2].split(' [H> ') if '[H>' in o else ('', '')
    exp_l = l + '1' + '10' * s + '1' + '10' * (d - 1); exp_r = '1111' + '10' * (6 * R + 3) + '0' + '101' * (k + 3) + '11100100' * t + '101'
    if not (o.startswith('HALT1') and expand(left).lstrip('0') == exp_l and expand(right).rstrip('0') == exp_r):
        bad += 1; print('H0 FAIL', dict(s=s, d=d, k=k, R=R, t=t), o[:150])
print('bad', bad)
