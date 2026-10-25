# ktslots.py: which transition slots do the record engine's rules R1, R2, R3 read?
# Literal runs of the record machine from Kt instances until the next Kt-moment (state B, head on the blank right of
# the word, i.e. every cell right of the head is 0).  Union of slots over many small parameter values.
REC = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_0RH0RF_0RG0RE_0LH---'
def parse(m):
    T = {}
    for q, row in enumerate(m.split('_')):
        for c in (0, 1):
            x = row[3*c:3*c+3]
            T[(q, c)] = None if '-' in x or x[2] == 'Z' else (int(x[0]), 1 if x[1] == 'R' else -1, ord(x[2]) - 65)
    return T
def kt(ds, m, r, t):   # tape string (left to right), head index (on the blank right of the word)
    left = '11' + ''.join('10' * d + '1' for d in reversed(ds)) + '10' * m + '1' + '10' * r + '11' + '11111100' * t + '1001'
    return left
def run(T, ds, m, r, t, maxs=10**6):
    s = kt(ds, m, r, t); tape = dict((i, int(ch)) for i, ch in enumerate(s)); pos = len(s); q = 1; used = set(); n = 0
    while n < maxs:
        c = tape.get(pos, 0); tr = T[(q, c)]; used.add((q, c))
        if tr is None: return used, 'halt'
        w, d, nq = tr; tape[pos] = w; pos += d; q = nq; n += 1
        if q == 1 and all(v == 0 for k, v in tape.items() if k >= pos) and n > 2: return used, n
    return used, 'budget'
T = parse(REC); U = {}
for name, cases in (('R1', [([4], m, r, t) for m in (3, 4, 5, 6, 7) for r in (1, 2, 5) for t in (0, 1, 2)]),
                    ('R2', [([3 + x], 1, r, t) for x in (0, 1, 2, 4) for r in (1, 2, 5) for t in (0, 1, 2)]),
                    ('R3', [([1] * (k + 1) + [3 + x], 1, r, t) for k in (0, 1, 2) for x in (1, 2, 4) for r in (1, 2, 5) for t in (0, 1, 2)])):
    u = set()
    for c in cases:
        used, n = run(T, *c); u |= used
        assert n != 'halt' and n != 'budget', (name, c, n)
    U[name] = u
    print(name, sorted('%s%d' % (chr(65 + q), s) for q, s in u))
allu = set().union(*U.values())
print('union', len(allu), ' '.join(sorted('%s%d' % (chr(65 + q), s) for q, s in allu)))
