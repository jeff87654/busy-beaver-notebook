import re, random
from fractions import Fraction as F
rows = []
for fn in ['tmp/chgrid1.txt', 'tmp/chgrid2.txt']:
    for line in open(fn):
        m = re.match(r'(\d+) \[([\d, ]+)\] HALT \(\'I\', 0\) (\d+) (.*)', line)
        if not m:
            continue
        B = int(m.group(1)); fk = [int(x) for x in m.group(2).split(',')]; ones = int(m.group(3)); sig = m.group(4)
        sig = re.sub(r'S\(\d+\)', 'S', sig); sig = re.sub(r'CLR\(D[^\]]*\]*', 'CLR', sig)
        rows.append((B, fk, ones, sig))
print(len(rows), 'rows; distinct signatures (S counts ignored):', len(set(r[3] for r in rows)))
for s in sorted(set(r[3] for r in rows)):
    print('   ', [r[0] for r in rows if r[3] == s], s[:200])
X = [[1, r[0]] + r[1][:6] for r in rows]; y = [r[2] for r in rows]
def solve(M, v):
    k = len(M); M = [list(map(F, r)) + [F(x)] for r, x in zip(M, v)]
    for i in range(k):
        p = next(r for r in range(i, k) if M[r][i] != 0); M[i], M[p] = M[p], M[i]
        for r in range(k):
            if r != i and M[r][i] != 0:
                f = M[r][i] / M[i][i]; M[r] = [a - f * b for a, b in zip(M[r], M[i])]
    return [M[i][k] / M[i][i] for i in range(k)]
rng = random.Random(1)
c = None
for _ in range(2000):
    idx = rng.sample(range(len(rows)), 8)
    try:
        c = solve([X[i] for i in idx], [y[i] for i in idx]); break
    except StopIteration:
        continue
print('ones = %s + %s*B + %s*F1 + %s*F2 + %s*F3 + %s*F4 + %s*F5 + %s*F6' % tuple(c))
print('misfits:', sum(1 for r, yy in zip(X, y) if sum(a * b for a, b in zip(c, r)) != yy), 'of', len(rows))
