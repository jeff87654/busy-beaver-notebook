"""CORRECT 6-state fold: keep the halt 2.

A2 = 2LX  (the halt cell stays 2, so the core's halt detector survives the fold)
X2 = 1LX, X3 = 2LX, X0 = 3RY
Y2 = 2RY, Y1 = 1LW
W2 = 2RA  -> lands on the FIRST 1 in state A

   3^(2m+1) 2^k A> 2  --fold-->  3 2^(2m+1) A> 1^k 2
i.e. B(k, 0, m) -> B(2m+1, k, 0) with the trailing halt 2 preserved  -> the chain can repeat.
"""
STATES = 'ABCXYW'
A6 = '1RB3LB2LX2RA'
B6 = '2LC3RB1LC2RA'
C6 = '3RB1LB3LC2RC'
X6 = '3RY0LX1LX2LX'
Y6 = '0RY1LW2RY0RY'
W6 = '0LA0LA2RA0LA'
FOLD6 = '_'.join([A6, B6, C6, X6, Y6, W6])
PLAIN = '_'.join(['1RB3LB1RZ2RA', B6, C6])


def parse(s):
    return [[blk[3*i:3*i+3] for i in range(len(blk)//3)] for blk in s.split('_')]


def cfg(tape, pos):
    i = pos-1; a = 0
    while tape.get(i, 0) == 2: a += 1; i -= 1
    b = 0
    while tape.get(i, 0) == 3: b += 1; i -= 1
    j = pos; n = 0
    while tape.get(j, 0) == 1: n += 1; j += 1
    return b, a, n, tape.get(j, 0)


def mk(m, k, tail=2, zeros=24, base=100):
    tape = {}; pos = base
    for _ in range(2*m+1): tape[pos] = 3; pos += 1
    for _ in range(k): tape[pos] = 2; pos += 1
    head = pos
    tape[pos] = tail; pos += 1
    for _ in range(zeros): tape[pos] = 0; pos += 1
    return tape, head


def run_fold(m, k, cap, nmax=8):
    tape, head = mk(m, k)
    tab = parse(FOLD6); pos, st = head, 'A'; ev = []
    for s in range(1, cap+1):
        if st == 'A' and tape.get(pos, 0) == 2:
            ev.append((s,) + cfg(tape, pos))
            if len(ev) >= nmax:
                return ev, ('MORE', s)
        tr = tab[STATES.index(st)][tape.get(pos, 0)]
        if tr[0] == '-':
            return ev, ('UNDEF', s)
        tape[pos] = int(tr[0]); pos += 1 if tr[1] == 'R' else -1; st = tr[2]
        if st == 'Z':
            return ev, ('HALT', s)
    return ev, ('TIME', cap)


print('=== does the chain repeat?  (trigger configs: 3-run, 2-run, 1-run, cell-right-of-1s) ===')
for (m, k) in [(0, 1), (0, 2), (1, 1), (1, 2), (2, 2), (3, 1)]:
    ev, res = run_fold(m, k, 3000000)
    print(f'(m={m},k={k}) {res}   folds={len(ev)}')
    for e in ev[:6]:
        print(f'    step={e[0]:8d}  3-run={e[1]} (m={(e[1]-1)//2})  2-run={e[2]} (k={e[2]})  '
              f'1-run={e[3]}  right-of-1s={e[4]}')

print()
print('=== orbit identity with plain core at B(2m+1,k,0) (tail 2 = 2) ===')
for (m, k) in [(0, 1), (0, 3), (1, 2), (2, 3)]:
    tape, head = mk(m, k)
    tab = parse(FOLD6); pos, st = head, 'A'
    for s in range(1, 500):
        tr = tab[STATES.index(st)][tape.get(pos, 0)]
        tape[pos] = int(tr[0]); pos += 1 if tr[1] == 'R' else -1; st = tr[2]
        if st == 'A' and tape.get(pos, 0) == 1:
            break
    out = cfg(tape, pos)
    ta, ha = mk(0, 2*m+1)             # B(2m+1, 0, 0) + tail 2  is NOT right; build B(2m+1,k,0):
    ta = {}; q = 100
    for _ in range(1): ta[q] = 3; q += 1
    for _ in range(2*m+1): ta[q] = 2; q += 1
    hb = q
    for _ in range(k): ta[q] = 1; q += 1
    ta[q] = 2; q += 1
    for _ in range(24): ta[q] = 0; q += 1
    pb = parse(PLAIN); pa, sa = hb, 'A'; tb = dict(tape); pf, sf = pos, 'A'
    n = 0; end = None
    while n < 200000:
        if (sa, cfg(ta, pa)) != (sf, cfg(tb, pf)):
            end = ('DIFF', n); break
        n += 1
        tr = pb['ABC'.index(sa)][ta.get(pa, 0)]
        if tr[2] == 'Z':
            end = ('plain HALT', n); break
        ta[pa] = int(tr[0]); pa += 1 if tr[1] == 'R' else -1; sa = tr[2]
        tr = tab[STATES.index(sf)][tb.get(pf, 0)]
        tb[pf] = int(tr[0]); pf += 1 if tr[1] == 'R' else -1; sf = tr[2]
    print(f'(m={m},k={k}): fold output={out} (predicted (1,{2*m+1},{k},2)); identical {n} steps then {end}')
