"""Exact literal checks of the rules of
  R1 = 1RB1LF_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RA1LG_---0LH_1RA0LF
  R2 = 1RB0LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RA1LG_---0LH_1RA0LF
Every start is  0^inf A>0 <lhs> r 0^inf  with r a random bit word (tail 0: r empty).  We run with no
acceleration until the first configuration  0^inf A>0 <rhs> r 0^inf  (checked at every step where A reads 0
with blank tape to its left) or, for halting rules, until the machine halts; we require the exact predicted
tape INCLUDING r at its original absolute position, that no cell of r was ever visited, and record the step
count (for rules with a formula, the formula is checked too).

usage: python check_R.py R1|R2 [--pmax 100] [--tails 3] [--qmaxZZ 4] [--out file.json]
"""
import sys, random, json, argparse
from fractions import Fraction
from lit import parse, ST

TMS = {'R1': "1RB1LF_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RA1LG_---0LH_1RA0LF",
       'R2': "1RB0LG_1RC0RE_1LD1LC_1LA0LD_1LB1RF_1RA1LG_---0LH_1RA0LF"}
ap = argparse.ArgumentParser()
ap.add_argument('machine')
ap.add_argument('--pmax', type=int, default=100)
ap.add_argument('--tails', type=int, default=3)
ap.add_argument("--qmaxZZ", type=int, default=4)
ap.add_argument("--qmax", type=int, default=100)
ap.add_argument('--out', default=None)
args = ap.parse_args()
TM = TMS[args.machine]
T = parse(TM)
random.seed(20260927)

def run(lhs, r, rhs, halt, maxsteps):
    """Returns (ok, steps, msg)."""
    word = lhs + r
    n = len(word)
    pad = 2 * n + 2 * len(rhs) + 64
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(pad)
    start = pad - 1                   # head starts on the blank cell left of the word
    rstart = pad + len(lhs)           # absolute index of first cell of r
    target = bytes(int(c) for c in rhs + r)
    pos = start; st = 0; steps = 0; maxpos = pos; lo = pos
    tlen = len(tape)
    hpos = rstart - 1 - len(rhs)      # predicted final head position
    while steps < maxsteps:
        s = tape[pos]
        e = T[st][s]
        if e is None:
            if not halt:
                return (False, steps, 'unexpected HALT state %s' % ST[st])
            ok = (st == 6 and s == 0 and not any(tape[:pos]) and pos + 1 + len(rhs) == rstart
                  and bytes(tape[pos + 1:pos + 1 + len(target)]) == target and not any(tape[pos + 1 + len(target):])
                  and maxpos < rstart)
            return (ok, steps, 'halt state %s read %d maxpos-rstart %d' % (ST[st], s, maxpos - rstart))
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos > maxpos: maxpos = pos
        if pos <= 0 or pos >= tlen - 1:
            return (False, steps, 'tape overflow')
        if pos < lo: lo = pos
        if pos == hpos and st == 0 and tape[pos] == 0 and not halt:
            # cells left of lo were never visited, hence blank
            if not any(tape[lo:pos]) and bytes(tape[pos + 1:pos + 1 + len(target)]) == target \
                    and not any(tape[pos + 1 + len(target):]):
                return (maxpos < rstart, steps, 'match, maxpos-rstart %d' % (maxpos - rstart))
    return (False, steps, 'step limit')

def rtail():
    L = random.randint(1, 12)
    return ''.join(random.choice('01') for _ in range(L))

def fitpoly(pts, deg):
    """Exact Lagrange fit through first deg+1 points; returns coeff list (Fractions, low->high) or None if
    it does not fit all points."""
    xs = [Fraction(x) for x, _ in pts[:deg + 1]]; ys = [Fraction(y) for _, y in pts[:deg + 1]]
    if len(xs) < deg + 1: return None
    # solve Vandermonde
    import itertools
    m = deg + 1
    A = [[x ** k for k in range(m)] + [y] for x, y in zip(xs, ys)]
    for c in range(m):
        piv = next(i for i in range(c, m) if A[i][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        for i in range(m):
            if i != c and A[i][c] != 0:
                f = A[i][c] / A[c][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[c])]
    coef = [A[i][m] / A[i][i] for i in range(m)]
    for x, y in pts:
        if sum(c * Fraction(x) ** k for k, c in enumerate(coef)) != y:
            return None
    return coef

def polystr(coef, var):
    terms = []
    for k in range(len(coef) - 1, -1, -1):
        c = coef[k]
        if c == 0: continue
        cs = str(c)
        terms.append(cs if k == 0 else ('%s*%s^%d' % (cs, var, k) if k > 1 else '%s*%s' % (cs, var)))
    return ' + '.join(terms) if terms else '0'

P = args.pmax
Q = args.qmax
o = lambda k: '1' * k
z = lambda k: '0' * k
# name: (param name, param range, lhs(x), rhs(x), halt?, closed-form step count(x) -- checked exactly)
COMMON = {
    'O':  ('p', range(0, P), lambda p: o(2*p+1) + '0', lambda p: o(2*p+5), False, lambda p: 8*p + 9),
    'D':  ('p', range(1, P), lambda p: o(2*p) + '0010', lambda p: '1' + z(2*p-1) + o(6), False, lambda p: 8*p + 8),
    'C2': ('p', range(0, P), lambda p: o(2*p+1) + '010010', lambda p: o(8*p+27), False, lambda p: 32*p*p + 178*p + 246),
}
R1RULES = {
    'D1':  ('p', range(1, P), lambda p: o(2*p) + '001110', lambda p: '1' + z(2*p-1) + o(8), False, lambda p: 8*p + 16),
    'E1':  ('p', range(1, P), lambda p: o(2*p) + '010010', lambda p: '1' + z(2*p+1) + o(6), False, lambda p: 8*p + 18),
    'E1b': ('p', range(1, P), lambda p: o(2*p) + '01001110', lambda p: '1' + z(2*p+1) + o(8), False, lambda p: 8*p + 26),
    'C1':  ('p', range(0, P), lambda p: o(2*p+1) + '010011100001', lambda p: o(8*p+42), False, lambda p: 32*p*p + 274*p + 665),
    'Z2':  ('q', range(1, Q), lambda q: o(6*q+2) + z(4), lambda q: o(6) + '001' * (2*q-1) + '11' + '00001', False, lambda q: 24*q + 22),
    'Z4':  ('q', range(1, Q), lambda q: o(6*q+4) + z(4), lambda q: o(6) + '010' * (2*q-1) + '0111' + '00001', False, lambda q: 24*q + 32),
    'Z0':  ('q', range(1, Q), lambda q: o(6*q) + z(4), lambda q: '100' * (2*q-1) + '111' + '00001', True, lambda q: 24*q + 5),
    'ZZ2': ('q', range(1, args.qmaxZZ + 1), lambda q: o(6*q+2) + z(4), lambda q: o((26 * 4**q + 22) // 3), False, lambda q: Fraction(5408*16**q, 135) - Fraction(1066*4**q, 27) + Fraction(896*q, 9) + Fraction(5374, 45)),
    'ZZ4': ('q', range(1, args.qmaxZZ + 1), lambda q: o(6*q+4) + z(4), lambda q: o((32 * 4**q + 22) // 3), False, lambda q: Fraction(8192*16**q, 135) - Fraction(1312*4**q, 27) + Fraction(896*q, 9) + Fraction(6116, 45)),
}
R2RULES = {
    'E2':  ('p', range(1, P), lambda p: o(2*p) + '01', lambda p: '1' + z(2*p+2) + '1', False, lambda p: 8*p + 8),
    'C0':  ('p', range(0, P), lambda p: o(2*p+1) + '001', lambda p: o(2*p+10), False, lambda p: 16*p + 34),
    'Z4':  ('q', range(1, Q), lambda q: o(6*q+4) + z(4), lambda q: o(6) + '001' * (2*q-1) + '0001' + '00001', False, lambda q: 24*q + 30),
    'Z0':  ('q', range(1, Q), lambda q: o(6*q) + z(4), lambda q: o(6) + '010' * (2*q-2) + '001' + '00001', False, lambda q: 24*q + 16),
    'Z2':  ('q', range(0, Q), lambda q: o(6*q+2) + z(4), lambda q: '100' * (2*q) + '01' + '00001', True, lambda q: 24*q + 13),
    'ZZ4': ('q', range(1, args.qmaxZZ + 1), lambda q: o(6*q+4) + z(4), lambda q: o((26 * 4**q + 4) // 3) + '00001', False, lambda q: Fraction(5408*16**q, 135) - Fraction(2002*4**q, 27) + Fraction(896*q, 9) + Fraction(4009, 45)),
    'ZZ0': ('q', range(2, args.qmaxZZ + 1), lambda q: o(6*q) + z(4), lambda q: o((110 * 4**(q-1) + 4) // 3) + '00001', False, lambda q: Fraction(1210*16**q, 27) - Fraction(4235*4**q, 54) + Fraction(896*q, 9) + Fraction(2035, 9)),
}
RULES = dict(COMMON); RULES.update(R1RULES if args.machine == 'R1' else R2RULES)

res = {}
allok = True
for name, (var, rng, lf, rf, halt, sf) in RULES.items():
    ok = bad = 0
    steps = {}
    ntails = args.tails if not name.startswith('ZZ') else 2
    for x in rng:
        lhs, rhs = lf(x), rf(x)
        for t in range(ntails):
            r = '' if t == 0 else rtail()
            good, st, msg = run(lhs, r, rhs, halt, 10**9)
            if good and x in steps and steps[x] != st:
                good = False; msg = 'step count depends on r'
            if good and st != sf(x):
                good = False; msg = 'step count %d != formula %s' % (st, sf(x))
            if good:
                ok += 1; steps[x] = st
            else:
                bad += 1
                print('FAIL', name, var, x, repr(r), msg)
    pts = sorted(steps.items())
    fit = None; fs = ''
    if not name.startswith('ZZ'):
        for deg in range(1, 4):
            fit = fitpoly(pts, deg)
            if fit: break
        fs = (polystr(fit, var) if fit else 'no poly fit deg<=3') + '  (= formula at every point)'
    else:
        fs = 'steps ' + ', '.join('%s=%d:%d' % (var, x, s) for x, s in pts)
    res[name] = dict(ok=ok, bad=bad, range=[min(rng), max(rng)], steps=steps, stepfit=fs)
    allok &= bad == 0
    print('%-4s %s=%d..%d  %5d ok %d fail   steps = %s' % (name, var, min(rng), max(rng), ok, bad, fs))
    sys.stdout.flush()
print('ALL OK' if allok else 'FAILURES')
if args.out:
    json.dump(dict(tm=TM, results=res), open(args.out, 'w'), indent=1)
