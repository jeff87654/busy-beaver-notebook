import re, itertools
from fractions import Fraction as F
R = []
for fn in ['tmp/realj366.txt', 'tmp/realj366b.txt']:
    for l in open(fn):
        m = re.match(r'(\d+) \[([\d, ]+)\] HALT \(.I., 0\) (\d+)', l)
        if m:
            R.append(([int(x) for x in m.group(2).split(',')], int(m.group(3))))
print(len(R), 'rows')
def solve(M, v):
    k = len(M); M = [list(map(F, r)) + [F(x)] for r, x in zip(M, v)]
    for i in range(k):
        p = next(r for r in range(i, k) if M[r][i] != 0); M[i], M[p] = M[p], M[i]
        for r in range(k):
            if r != i and M[r][i] != 0:
                f = M[r][i] / M[i][i]; M[r] = [a - f * b for a, b in zip(M[r], M[i])]
    return [M[i][k] / M[i][i] for i in range(k)]
c = None
for idx in itertools.combinations(range(len(R)), 7):
    try:
        c = solve([R[i][0] + [1] for i in idx], [R[i][1] for i in idx]); break
    except StopIteration:
        continue
if c:
    print('ones = %s*F1 + %s*F2 + %s*F3 + %s*F4 + %s*F5 + %s*F6 + %s  (B=366)' % tuple(c))
    print('misfits', sum(1 for fk, o in R if sum(a * b for a, b in zip(c, fk + [1])) != o), 'of', len(R))
else:
    print('singular')
