# ktcheck.py [--allq] MACHINE... : literal check of the record engine rules R1-R3 (Kt level) on small instances.
#   Kt ds m r t = 0^inf 11 D(d_n)..D(d_1) D(m) (10)^r 11 (11111100)^t 1001 Q> 0^inf,  D(x) = (10)^x 1, Q = B (or each state)
import sys
def parse(m):
    T = {}
    for q, row in enumerate(m.split('_')):
        for c in (0, 1):
            x = row[3*c:3*c+3]
            T[(q, c)] = None if '-' in x or x[2] == 'Z' or ord(x[2]) - 65 >= len(m.split('_')) else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
def kt(ds, m, r, t):
    return '11' + ''.join('10' * d + '1' for d in reversed(ds)) + '10' * m + '1' + '10' * r + '11' + '11111100' * t + '1001'
def runto(T, start, target, Q, maxs=200000):
    s = kt(*start); tape = dict((i, int(ch)) for i, ch in enumerate(s)); pos = len(s); q = Q; n = 0; tgt = kt(*target)
    while n < maxs:
        tr = T[(q, tape.get(pos, 0))]
        if tr is None: return False
        w, d, nq = tr; tape[pos] = w; pos += d; q = nq; n += 1
        if q == Q and all(v == 0 for k, v in tape.items() if k >= pos):
            lo = min(k for k, v in tape.items() if v)
            if ''.join(str(tape.get(i, 0)) for i in range(lo, pos)) == tgt: return True
    return False
cases = {'R1': [(([4], 3 + m, r, t), ([4], m, 2 * r + 4, t)) for m in (0, 1, 2, 4) for r in (1, 2, 5) for t in (0, 1, 2)],
         'R2': [(([3 + x, 4], 1, r, t), ([x, 4], 2 * r + 3, 2, t)) for x in (0, 1, 2, 4) for r in (1, 2, 5) for t in (0, 1, 2)],
         'R3': [(([1] * (k + 1) + [3 + x, 4], 1, r, t), ([1] * k + [2 * r + 3, x, 4], 1, 2, t)) for k in (0, 1, 2) for x in (1, 2, 4) for r in (1, 2, 5) for t in (0, 1, 2)]}
allq = '--allq' in sys.argv
for m in [a for a in sys.argv[1:] if not a.startswith('--')]:
    T = parse(m)
    for Q in (range(len(m.split('_'))) if allq else [1]):
        print(m, chr(65 + Q), ' '.join(f'{n}:{sum(runto(T, a, b, Q) for a, b in cs)}/{len(cs)}' for n, cs in cases.items()))
