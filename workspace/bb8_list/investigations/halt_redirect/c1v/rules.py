"""rules.py: literal checks of the champion rules R1-R3 (GH token form) for c1, with head confinement and slot usage.
R1 [L | a | r]            -> [L | a-3 | 2r+5]                 a >= 4
R2 [L, d | 1 | r]         -> [L, d-3 | 2r+5 | 1]              d >= 3 (d = 3 reported separately)
R3 [L, d, 1^k | 1 | r]    -> [L, d-3, 2r+5, 1^(k-1) | 1 | 1]  k >= 1
L ranges over the left contexts that occur in c1's run.  Head confinement: the head never moves left of the first cell of
the leftmost pattern token minus 1 (that cell is the final 1 of L's last token), so the rule holds for every nonempty L."""
import random, sys, collections
import c1lib
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
CTX = [[6] * 5, [6] * 3 + [4], [6] * 4 + [3], [6] * 2 + [0], [6] * 3 + [2, 0], [6] * 2 + [3, 2, 1, 0], [6] * 6 + [2, 2, 0],
       [6] * 2 + [3, 3, 1, 1], [6] * 7 + [3, 0], [6], [6, 0]]
def rvals():
    return random.choice([1, 4, 7, 19, 1 + 3 * random.randint(0, 60), 1 + 3 * random.randint(0, 900), 2539, 5059, 7579,
                          49612750485498 % 7200 + 1])
stats = collections.Counter(); bad = []; slots = collections.Counter()
def check(name, L, pat, tgt):
    toks = L + pat; f = c1lib.reach(toks, L + tgt, maxs=4 * 10**8)
    start_cell = len(c1lib.word(L)) - 4          # first cell of the leftmost pattern token
    ok = f[0] == 'REACHED' and int(f[2]) >= start_cell - 1
    stats[(name, ok)] += 1
    if f[0] == 'REACHED': slots[(name, f[3])] += 1
    if not ok: bad.append((name, L, pat, " ".join(f))); print("BAD", name, L, pat, f, flush=True)
for it in range(int(sys.argv[2]) if len(sys.argv) > 2 else 150):
    L = random.choice(CTX); r = rvals()
    a = random.choice([4, 7, 10, 13, 43, 3 * random.randint(1, 40) + 1, random.randint(4, 60)])
    check('R1', L, [a, r], [a - 3, 2 * r + 5])
    d = random.choice([4, 5, 6, 7, 8, 9, 10, 41, 42, 43, random.randint(4, 200)])
    check('R2', L, [d, 1, r], [d - 3, 2 * r + 5, 1])
    k = random.choice([1, 2, 3, 5, 13, random.randint(1, 60), random.randint(100, 400)])
    check('R3', L, [d] + [1] * k + [1, r], [d - 3, 2 * r + 5] + [1] * (k - 1) + [1, 1])
for d in (3,):
    for L in CTX:
        for r in (1, 19, 2539):
            check('R2d3', L, [d, 1, r], [d - 3, 2 * r + 5, 1])
            for k in (1, 2, 7, 40):
                check('R3d3', L, [d] + [1] * k + [1, r], [d - 3, 2 * r + 5] + [1] * (k - 1) + [1, 1])
print(dict(stats)); print(dict(slots))
for b in bad[:30]: print('BAD', b)
print('TOTAL_BAD', len(bad))
