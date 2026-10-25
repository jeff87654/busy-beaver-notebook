"""pinc.py MACHINE STATE RUNS STEPS MAXP [MODE]
P-inclusive probe: tape = 1^r1 0 1^r2 0 ... 0 1^rk (RUNS comma list, 'x^n' = n copies), head in STATE on the blank right
of it. Prints the run list at each event 'head in STATE on a blank right of every 1' (MAXP events) or HALT steps ones.
MODE 'last': print only the final event / halt."""
import idle  # noqa
import sys
M, Q, RUNS, steps, maxp = sys.argv[1], ord(sys.argv[2]) - 65, sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
mode = sys.argv[6] if len(sys.argv) > 6 else 'all'
tr = {}
for q, blk in enumerate(M.split('_')):
    for c in range(2):
        t = blk[3*c:3*c+3]
        tr[(q, c)] = None if t[0] == '-' else (int(t[0]), 1 if t[1] == 'R' else -1, ord(t[2]) - 65)
runs = []
for x in RUNS.split(','):
    if '^' in x:
        v, n = x.split('^'); runs += [int(v)] * int(n)
    else:
        runs.append(int(x))
w = '0'.join('1' * r for r in runs)
SZ = 1 << 24
T = bytearray(SZ); off = SZ // 2
for i, ch in enumerate(w): T[off + i] = ch == '1'
p = off + len(w); q = Q; lo = off; hi = off + len(w) - 1; np_ = 0
def rl(r):
    o = []; i = 0
    while i < len(r):
        j = i
        while j < len(r) and r[j] == r[i]: j += 1
        o.append('%d' % r[i] + ('^%d' % (j - i) if j > i + 1 else '')); i = j
    return '[' + ','.join(o) + ']'
last = None
for st in range(steps):
    c = T[p]
    t = tr[(q, c)]
    if t is None:
        print('HALT', st, 'ones', sum(T)); last = None; break
    T[p] = t[0]
    if t[0]:
        lo = min(lo, p); hi = max(hi, p)
    p += t[1]; q = t[2]
    if p <= 1 or p >= SZ - 2:
        print('TAPE'); break
    if q == Q and T[p] == 0 and p > hi:
        while hi > lo and not T[hi]: hi -= 1
        if p > hi:
            while lo < hi and not T[lo]: lo += 1
            s = bytes(T[lo:hi + 1]).replace(b'\x00', b'0').replace(b'\x01', b'1').decode()
            ev = '%d gap %d %s' % (st + 1, p - hi - 1, rl([len(x) for x in s.split('0')]))
            if mode == 'all': print(ev)
            last = ev
            np_ += 1
            if np_ >= maxp: break
else:
    print('T')
if mode == 'last' and last: print(last)
