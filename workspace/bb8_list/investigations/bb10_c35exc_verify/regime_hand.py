"""regime_hand.py -- test the hand rules of rules.py across magnitude regimes (token a, accumulator y
small 4..30 or large 300..3000, all residues), with left context [P, 44, 3, 1, 1, 0, 31, 0]."""
import itertools, random
from lib import bforms, ctok, M10
P = [2, 1, 1, 0, 2, 1, 0, 1]
CTX = P + [44, 3, 1, 1, 0, 31, 0]
rnd = random.Random(9)
T = [  # (name, lhs, rhs) ; a = big token, y = accumulator ; 1^k with k in 1..3, 1^j with j in 1..2
 ('R1', 'a,0,y', 'a-3,0,2*y+8'),
 ('R2', 'a,1^k,0,y', 'a-3,y+3,1^(k-1),0,4'),
 ('S0a', 'a,0,0,y', 'a-4,3,0,2*y+4'),
 ('S0b', 'a,0,1^k,0,y', 'a-4,3,y+1,1^(k-1),0,4'),
 ('S0j0', 'a,1^j,0,0,y', 'a-4,3,1^j,0,2*y+4'),
 ('S0jk', 'a,1^j,0,1^k,0,y', 'a-4,3,1^j,y+1,1^(k-1),0,4'),
 ('S0w3', 'a,3,0,1^k,0,y', 'a-3,5,y,1^k,0,4'),
 ('S0w3k0', 'a,3,0,0,y', 'a-3,5,y,0,4'),
 ('S0w2', 'a,2,1^j,0,0,y', 'a-3,4,0,1^j,0,2*y+4'),
 ('S0w2k', 'a,2,1^j,0,1^k,0,y', 'a-3,4,0,1^j,y+1,1^(k-1),0,4'),
 ('S0w2u0', 'a,0,2,1^j,0,0,y', 'a-4,3,2,0,1^j,0,2*y+4'),
 ('S0w2u0v0', 'a,0,0,2,1^j,0,0,y', 'a-4,2,0,3,0,1^j,0,2*y+4'),
 ('S0w0', 'a,0,0,0,y', 'a-4,2,0,0,2*y+6'),
 ('S0w0k', 'a,0,0,1^k,0,y', 'a-4,2,0,y+2,1^(k-1),0,4'),
 ('S0w3u0', 'a,0,3,0,1^k,0,y', 'a-4,3,3,y,1^k,0,4'),
 ('S0w3u0k0', 'a,0,3,0,0,y', 'a-4,3,3,y,0,4'),
 ('S0w3u0v2', 'a,2,0,3,0,0,y', 'a-3,4,0,3,y,0,4'),
 ('S0j1w3u0', 'a,0,3,1,0,0,y', 'a-3,y+6,1,0,4'),
 ('S2', 'a,2,1^k,0,y', 'a-3,y+4,1^k,0,6'),
 ('S2k0', 'a,2,0,y', 'a-3,y+4,0,6'),
 ('S2w1', 'a,1,2,1^k,0,y', 'a-3,y+5,0,1^k,0,6'),
 ('S2w0', 'a,1^j,0,2,1^k,0,y', 'a-4,3,1^j,y+2,1^k,0,6'),
 ('S2w0b', 'a,0,2,0,y', 'a-4,3,y+2,0,6'),
 ('S2w2', 'a,2,2,0,y', 'a-1,y+1,5,0,4'),
]
def expand(pat, env):
    out = []
    for tok in pat.split(','):
        if tok == '1^j': out += [1] * env['j']
        elif tok == '1^k': out += [1] * env['k']
        elif tok == '1^(k-1)': out += [1] * (env['k'] - 1)
        else: out.append(int(eval(tok, {}, env)))
    return out
for name, lhs, rhs in T:
    fails = []; tot = 0
    for ra, ry in itertools.product('SL', repeat=2):
        for trial in range(3):
            a = rnd.randint(5, 30) if ra == 'S' else rnd.randint(300, 3000)
            y = rnd.randint(4, 30) if ry == 'S' else rnd.randint(300, 3000)
            env = dict(a=a, y=y, j=rnd.randint(1, 2), k=rnd.randint(1, 3))
            L = CTX + expand(lhs, env); E = CTX + expand(rhs, env)
            bf, end = bforms(M10, L, 4 * 10**7, maxsnap=2)
            got = bf[1][1] if len(bf) > 1 else None
            tot += 1
            if got != E: fails.append((ra + ry, env, ctok(got[len(CTX):]) if got else end[:2]))
    print('%-10s %s' % (name, 'OK %d' % tot if not fails else 'FAIL %d/%d' % (len(fails), tot)))
    for f in fails[:3]: print('      ', f)
