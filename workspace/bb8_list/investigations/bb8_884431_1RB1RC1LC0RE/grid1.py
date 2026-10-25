import itertools, sys
from rulecheck import next_family
# lists given nearest-first (L), converted to farthest-first for the machine
def nxt(L, a, b):
    r = next_family(L[::-1], a, b)
    if r[0] in ('HALT', 'TIMEOUT'): return r
    return (r[0], r[1][::-1], r[2], r[3])
def rule(L, a, b):
    if a > 0: return (list(L), a-1, b+1)
    if not L: return None
    # first nonzero
    k = 0
    while k < len(L) and L[k] == 0: k += 1
    if k == len(L): return ('R4', list(L), b)
    y1 = L[k]
    t = L[k+1:]
    if k == 0: return ([y1-1]+t, 2*b+3, 0)
    return ([1]*(k-1) + [2*b+3] + [y1-1] + t, 1, 0)   # k zeros skipped -> k-1 ones then big
bad = 0; tot = 0
for n in range(0, 4):
  for L in itertools.product(range(0, 4), repeat=n):
    L = list(L)
    for a in range(0, 3):
        for b in range(0, 6):
            tot += 1
            r = rule(L, a, b)
            if r is None: continue
            got = nxt(L, a, b)
            if r[0] == 'R4':
                exp = ([1]*0 + [0]*0, )  # skip compare here
                continue
            if got[0] in ('HALT','TIMEOUT') or (got[1], got[2], got[3]) != r:
                bad += 1
                if bad <= 25: print('MISMATCH', L, a, b, 'exp', r, 'got', got)
print('total', tot, 'bad', bad)
