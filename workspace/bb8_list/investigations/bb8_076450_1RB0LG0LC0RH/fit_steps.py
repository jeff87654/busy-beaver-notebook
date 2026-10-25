"""Fit exact (integer) linear step-count formulas to the literal rule checks (check_rules.json), and verify
that the formula reproduces every checked case."""
import json, re
from fractions import Fraction
from collections import defaultdict
res = json.load(open('check_rules.json'))
data = defaultdict(list)
for r in res:
    kind, arg = r['case'].split()
    nums = tuple(int(x) for x in re.findall(r'\d+', arg))
    data[kind].append((nums, r['steps']))

def solve(rows, feats):
    """Gaussian elimination over Q on a subset, then verify on all rows."""
    m = len(feats)
    A = []; 
    for n, s in rows:
        A.append([Fraction(f(*n)) for f in feats] + [Fraction(s)])
    # pick independent rows greedily
    basis = []
    M = []
    for row in A:
        cand = M + [row]
        # rank check
        import copy
        B = [r[:m] for r in cand]
        rk = rank(B)
        if rk > len(M):
            M.append(row)
        if len(M) == m: break
    coef = gauss(M, m)
    bad = [(n, s) for n, s in rows if sum(c * f(*n) for c, f in zip(coef, feats)) != s]
    return coef, bad

def rank(B):
    B = [r[:] for r in B]; rk = 0; cols = len(B[0])
    for c in range(cols):
        piv = next((i for i in range(rk, len(B)) if B[i][c] != 0), None)
        if piv is None: continue
        B[rk], B[piv] = B[piv], B[rk]
        for i in range(len(B)):
            if i != rk and B[i][c] != 0:
                f = B[i][c] / B[rk][c]; B[i] = [x - f * y for x, y in zip(B[i], B[rk])]
        rk += 1
    return rk

def gauss(M, m):
    M = [r[:] for r in M]
    for c in range(m):
        piv = next(i for i in range(c, m) if M[i][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        for i in range(m):
            if i != c and M[i][c] != 0:
                f = M[i][c] / M[c][c]; M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return [M[i][m] / M[i][i] for i in range(m)]

one = lambda *n: 1
specs = {
    'R1': (['a', 'b', 'c', '1'], [lambda a, b, c: a, lambda a, b, c: b, lambda a, b, c: c, one]),
    'R2': (['a', 'c+1', '1'], [lambda a, z, c: a, lambda a, z, c: c, one]),
    'R3': (['a', '1'], [lambda a, z, y: a, one]),
    'R4': (['n', '1'], [lambda n: n, one]),
    'R5': (['n', '1'], [lambda n: n, one]),
    'R6': (['n', '1'], [lambda n: n, one]),
}
for k, (names, feats) in specs.items():
    coef, bad = solve(data[k], feats)
    print('%s: steps = %s   (%d cases, %d misfits)' % (k, ' + '.join('%s*%s' % (c, n) for c, n in zip(coef, names)), len(data[k]), len(bad)))
    if bad: print('   misfits', bad[:5])
print('R5s', data['R5s'], 'R5h', data['R5h'])
