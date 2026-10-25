"""random checks of the standard rules R1 / R2R3 / R2' (a-token 0) in general contexts"""
import random, sys
from fam import *
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 60
QS = ['', '101011100' + '100'*5, '101011100' + '100'*3 + '111010100', '110110101010100', '1101010101100' + '100'*2]
TAILS = [(3,[1]), (8,[1,1]), (8,[6,1,1]), (8,[6,6,1,1]), (3,[4,6,6,6,1,1])]
def predict(toks, r):
    a = toks[-1]
    if a >= 3: return ('R1', toks[:-1] + [a-3], 2*r+4)
    if a == 1:
        i = len(toks) - 2
        while i >= 0 and toks[i] == 1: i -= 1
        if i < 0 or toks[i] < 3: return None
        t = toks[:]; t[i] -= 3; t[i+1] = 2*r+3
        return ('R23', t, 2)
    if a == 0:
        i = len(toks) - 2
        if i < 0 or toks[i] < 4: return None
        t = toks[:-1]; t[i] -= 4; t.append(2*r+3)
        return ('R0', t, 2)
    return None
bad = 0; tot = 0
for it in range(N):
    Q = random.choice(QS); h, tail = random.choice(TAILS)
    k = random.randint(1, 5)
    toks = ([0,0] if random.random() < 0.5 else ([0,1] if random.random() < 0.5 else [])) + [random.choice([1,1,1,4,7,5,6,8,10,3,9]) for _ in range(k)]
    toks[-1] = random.choice([0,1,3,4,5,6,7,9,10])
    r = random.randint(1, 9)
    p = predict(toks, r)
    if p is None: continue
    tot += 1
    res = run(word_of(Q, toks, r, h, tail), 10**8, 1)
    c = res[0] if res else None
    ok = c is not None and 'toks' in c and c['toks'] == p[1] and c['r'] == p[2] and c['h'] == h and c['tail'] == tail
    if not ok:
        bad += 1; print('MISMATCH', p[0], Q[:20], toks, r, h, tail, '->', fmt(c) if c else None)
print(f'{tot} checked, {bad} mismatches')
