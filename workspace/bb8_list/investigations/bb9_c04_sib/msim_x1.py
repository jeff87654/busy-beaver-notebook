"""msim_x1.py : B-form macro simulator for X1 (n1 engine + I=---0RA) and siblings.
Config [ts | A] (ts far->near, n1 notation: tape = ... D(t) ... D0 D(A), state H on the blank right end).
CLR (n1 engine rule, Coq-proved for n1's engine A-H): [L, c+3d, 1^n | A] -> [L, c, 1^n | iter d (U n) A]; here the new A
is a REPRESENTATIVE (order-faithful policy A' = C + F*(n+1)*... , = 1 mod 3). Anything else = an EVENT, run literally
(lit_x1.Tape) to the next B-form.  Prints one line per event: before -> after.
  python msim_x1.py [--tm TM] [--A0 a] [--C c] [--F f] [--events N] [--maxlit S] [--quiet]"""
import sys, argparse, ctypes, lit_x1 as L
try: ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception: pass
ap = argparse.ArgumentParser()
ap.add_argument('--tm', default=None); ap.add_argument('--A0', type=int, default=7)
ap.add_argument('--C', type=int, default=5); ap.add_argument('--F', type=float, default=1.0)
ap.add_argument('--events', type=int, default=200); ap.add_argument('--maxlit', type=int, default=10**8)
ap.add_argument('--clrlog', action='store_true'); ap.add_argument('--brief', action='store_true'); ap.add_argument('--start', default=None)
a = ap.parse_args()
if a.tm:
    L.TMS = a.tm; L.T.clear()
    for qi, ch in enumerate(a.tm.split('_')):
        for s in (0, 1):
            e = ch[3*s:3*s+3]
            L.T[(L.QS[qi], s)] = None if e == '---' else (int(e[0]), 1 if e[1] == 'R' else -1, e[2])
def rep(n, d, A):
    R = 3 * (a.C + int(a.F * (n + 1))) + 1
    R = max(R, A + 3)            # accumulators only grow
    while R % 3 != 1: R += 1
    return R
def rle(ts):
    out = []; i = 0
    while i < len(ts):
        j = i
        while j < len(ts) and ts[j] == ts[i]: j += 1
        out.append(str(ts[i]) if j - i == 1 else '%d^%d' % (ts[i], j - i)); i = j
    return ' '.join(out)
# start: blank -> first B-form [7,1^35|4]
if a.start:
    f, A = a.start.split('|'); ts = []
    for x in f.split():
        if '^' in x: v, c = x.split('^'); ts += [int(v)] * int(c)
        else: ts.append(int(x))
    A = int(A)
else:
    ts, A = [7] + [1] * 35, 4
nev = 0; nclr = 0
while nev < a.events:
    # CLR?
    n = 0
    while n < len(ts) and ts[-1 - n] == 1: n += 1
    if n < len(ts) and ts[-1 - n] >= 3:
        x = ts[-1 - n]; d, c = divmod(x, 3)
        A2 = rep(n, d, A); ts[-1 - n] = c; nclr += 1
        if a.clrlog: print('  CLR n=%d x=%d A %d -> %d' % (n, x, A, A2))
        A = A2; continue
    before = '[%s | %d]' % (rle(ts), A)
    r = L.run_to_b(L.bword(ts, A), maxsteps=a.maxlit)
    nev += 1
    if r[0] != 'B':
        print('EV%d %s -> %s' % (nev, before, r[:2] + ((r[-1],) if r[0] == 'HALT' else ()))); break
    ts, A = [x for x in r[1] if isinstance(x, int) or True], r[2]
    if any(not isinstance(x, int) for x in ts):
        print('EV%d %s -> non-token tape %s' % (nev, before, L.fmt(r[1]))); break
    print('EV%d (clr %d) %s -> [%s | %d] steps %d' % (nev, nclr, before, rle(ts), A, r[3]), flush=True)
