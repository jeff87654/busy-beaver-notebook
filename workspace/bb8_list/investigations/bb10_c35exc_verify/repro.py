"""repro.py -- main results of bb10_c35exc_verify in one run (about 5 minutes at Idle).
  1. start-up reaches the record's B(5;[1]^36) = [4^36 | 0 | 16] (literal)
  2. real residues: T = 2^^37 3 mod M, y_f = 3T-8 = 0 mod 5; bb8-ab's B residue reproduced
  3. outer exhaustion [1^k,0,y] -> [2,1^(2y+4),0,1^(k-1),0,6] -> [P,6q+3,1^6q,0,5,1^k,0,4] (literal, y = 10..55)
  4. inner game [3T-6, 1^36, 0, 6] with the symbolic engine -> race configuration [.., a, 3, 1, 1, 0, 0, Y]
  5. race law: translated cycler iff Y < 2a+6 (literal, a = 12..30), and the real-magnitude representatives
"""
import random, pickle
from lib import run, bforms, tokens, ctok, word, M10
from num import H, M, res, is_huge
from tower import tower_res
import engine, rules, tcycler

P = [2, 1, 1, 0, 2, 1, 0, 1]

# 1
snaps, end = run(M10, '', 'A', '', 60000, ['snap=G0', 'bform'])
hit = [s[0] for s in snaps if tokens(s[1]) == [4] * 36 + [0, 16]]
print('1. [4^36|0|16] reached at step', hit[0] if hit else None)

# 2
N = 18101949465600
B = ((tower_res(2 * N) - 4) % (2 * N)) // 2
T = tower_res(M)
print('2. B mod N =', B, '(bb8-ab 16537583495166)', ' y_f mod 5 =', (3 * T - 8) % 5)

# 3
bad = 0
for y in (10, 25, 40, 55):
    for k in (1, 3, 36):
        bf, e = bforms(M10, [1] * k + [0, y], 5 * 10**7, maxsnap=3)
        q = y // 5
        e1 = [2] + [1] * (2 * y + 4) + [0] + [1] * (k - 1) + [0, 6]
        e2 = P + [6 * q + 3] + [1] * (6 * q) + [0, 5] + [1] * k + [0, 4]
        if [b[1] for b in bf[1:3]] != [e1, e2]:
            bad += 1
print('3. outer exhaustion formula mismatches:', bad)

# 4
A = H(3 * T - 6)
try:
    engine.R([A] + [1] * 36 + [0, 6], top=True)
    print('4. inner game finished (unexpected)')
except rules.Unknown as ex:
    lst = ex.lst
    print('4. inner game stops at (%d tokens):' % len(lst),
          ' '.join(('H%d' % res(v, 3)) if is_huge(v) else str(v) for v in lst))

# 5
row = []
for a in (12, 18, 24, 30):
    for Y in (2 * a, 2 * a + 4, 2 * a + 6, 2 * a + 10):
        toks = P + [44, 3, 1, 1, 0, 31, 0, a, 3, 1, 1, 0, 0, Y]
        tcycler.hist.clear()
        r = tcycler.check(M10, word(toks), 'G', '0', W=150, maxsteps=2 * 10**6)
        row.append('a=%d,Y=%d:%s' % (a, Y, 'TC' if r[0] == 'TCYCLER' else 'no'))
print('5. race law:', ' '.join(row))
