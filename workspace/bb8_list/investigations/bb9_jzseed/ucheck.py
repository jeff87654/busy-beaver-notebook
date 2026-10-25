# ucheck.py: jz.exe U residue law versus direct big-integer / tower arithmetic (independent of jz's tables).
#   U_0, U_1 exact (x <= 1500), U_1 of huge x == r mod MG (x = r + MG*10^40), iterates of U_0/U_1,
#   U_2(x) = U_1^(x-2)(91) for x <= 45 by recursive tower residues (no periodicity assumption),
#   Coq laws: Upar (U_j(x) == x+1 mod 2, x >= 2j) and U_mod8 (j >= 2: x even -> 7, x odd -> 0 mod 8) on jz's classes.
import subprocess, sys, os, random
from math import gcd
D = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(D, 'jz.exe')
def lam(n):   # Carmichael function
    res = 1; m = n; p = 2
    while p * p <= m:
        if m % p == 0:
            k = 0
            while m % p == 0: m //= p; k += 1
            l = (2 ** (k - 2) if k >= 3 else (1 if k == 1 else 2)) if p == 2 else (p - 1) * p ** (k - 1)
            res = res * l // gcd(res, l)
        p += 1
    if m > 1: res = res * (m - 1) // gcd(res, m - 1)
    return res
def U1x(x): return (21 * 3 ** x - 7) // 2
class Y:   # y_t = U_1^t(91); exact for t <= 1, residues by towers for larger t
    def __init__(s, t): s.t = t
    def mod(s, k):
        if k == 1: return 0
        if s.t == 0: return 91 % k
        if s.t == 1: return U1x(91) % k
        prev = Y(s.t - 1); L = lam(2 * k)
        e = prev.mod(L) + L * (64 // L + 2)            # prev is huge (>= 2^140 > log2(2k))
        return ((21 * pow(3, e, 2 * k) - 7) % (2 * k)) // 2
bad = 0
for MG in (2520, 27720, 720720):
    q = []; exp = []
    for x in list(range(0, 300)) + [random.randrange(300, 1500) for _ in range(40)]:
        q.append('U 0 %d' % x); exp.append(3 * x + 7)
        q.append('U 1 %d' % x); exp.append(U1x(x))
    for r in random.sample(range(MG), 60):
        x = r + MG * 10 ** 40; q.append('H 1 %d' % r); exp.append(('res', ((21 * pow(3, x, 2 * MG) - 7) % (2 * MG)) // 2))   # residue
        q.append('H 0 %d' % r); exp.append(('res', (3 * x + 7) % MG))
    for v in range(0, 12):
        for x in range(0, 8):
            y = x
            for _ in range(v): y = 3 * y + 7
            q.append('I 0 %d %d' % (v, x)); exp.append(y)
    for v in range(0, 4):
        for x in range(0, 5):
            y = x
            for _ in range(v): y = U1x(y) if y < 3000 else None; 
            if y is None: continue
            q.append('I 1 %d %d' % (v, x)); exp.append(y)
    for x in range(0, 46):
        t = max(0, x - 2); q.append('U 2 %d' % x); exp.append(('res', Y(t).mod(MG)) if t >= 2 else (91 if t == 0 else U1x(91)))
    out = subprocess.run([EXE, 'utab', '--mg', str(MG)], input='\n'.join(q) + '\n', capture_output=True, text=True).stdout.strip().split('\n')
    hdr = [l for l in out if not l.startswith(('U ', 'I ', 'H '))]; out = [l for l in out if l.startswith(('U ', 'I ', 'H '))]
    assert len(out) == len(q), (len(out), len(q))
    nb = 0
    for qq, o, e in zip(q, out, exp):
        f = o.split(); kind, val = f[-2], int(f[-1])
        if isinstance(e, tuple): ok = kind == 'huge' and val == e[1]
        elif e > 2 ** 100: ok = kind == 'huge' and val == e % MG
        else: ok = kind == 'exact' and val == e
        if not ok: nb += 1; print('MISMATCH', MG, qq, o, e[1] if isinstance(e, tuple) else e % MG)
    # Coq laws on huge classes, j = 2..8
    q2 = ['H %d %d' % (j, r) for j in range(2, 9) for r in range(0, MG, max(1, MG // 997))]
    out2 = subprocess.run([EXE, 'utab', '--mg', str(MG)], input='\n'.join(q2) + '\n', capture_output=True, text=True).stdout.strip().split('\n')
    out2 = [l for l in out2 if l.startswith('H ')]
    for qq, o in zip(q2, out2):
        j, r = int(qq.split()[1]), int(qq.split()[2]); val = int(o.split()[-1])
        if val % 2 != (r + 1) % 2: nb += 1; print('UPAR', MG, qq, o)
        if MG % 8 == 0 and val % 8 != (7 if r % 2 == 0 else 0): nb += 1; print('UMOD8', MG, qq, o)
    print('MG', MG, hdr[0], 'queries', len(q) + len(q2), 'mismatches', nb); bad += nb
print('TOTAL mismatches', bad)
