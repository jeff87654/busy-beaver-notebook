"""symx1.py : symbolic B-form simulator for n1-engine machines (X1 etc.), REAL-REGIME ordering.
Config [items | A]: items = ('t', aff) token D(aff) or ('r', aff) run of D1 tokens of length aff; A = aff.
aff = affine form over accumulator symbols (Fractions).  Symbols are ranked by creation; the ASSUMPTION is
"a newer accumulator >> every combination of older quantities" (towers; see notes.txt obs11 for when it fails).
CLR (n1 rule) [L, c+3d, 1^n | A] -> [L, c, 1^n | U_n^d A]: exact when everything is small, R1 (n=0) exact when d is a
small constant, otherwise a NEW top symbol (residue 40 mod 1260 for n >= 2 = tall-tower class).
Events: learned by probing (probe.py / msim2.exe) on a numeric instantiation that respects the symbolic order, then
fitting every output number as an affine function of the window's input numbers (one perturbation per input).
Learned rules are cached by key (window shape with small constants exact, residues mod 36 of the inputs, and the
order signature of the inputs).
  python symx1.py [--tm TM] [--events N] [--win K] [--log FILE]"""
import sys, argparse, itertools, json, os, subprocess
from fractions import Fraction as Fr
import probe
ap = argparse.ArgumentParser()
ap.add_argument('--tm', default=probe.X1); ap.add_argument('--events', type=int, default=200)
ap.add_argument('--win', type=int, default=7); ap.add_argument('--maxseg', type=float, default=3e10)
ap.add_argument('--gap', type=int, default=4); ap.add_argument('--base', type=int, default=40)
ap.add_argument('--show', type=int, default=40)
args = ap.parse_args()
MOD = 36
# ---------------------------------------------------------------- affine forms
class Aff:
    __slots__ = ('c', 'k')
    def __init__(self, c=0, k=None): self.c = Fr(c); self.k = {s: Fr(v) for s, v in (k or {}).items() if v != 0}
    def __add__(self, o):
        o = o if isinstance(o, Aff) else Aff(o); k = dict(self.k)
        for s, v in o.k.items(): k[s] = k.get(s, 0) + v
        return Aff(self.c + o.c, k)
    def __sub__(self, o): return self + (o if isinstance(o, Aff) else Aff(o)) * -1
    def __mul__(self, f): return Aff(self.c * f, {s: v * f for s, v in self.k.items()})
    def isc(self): return not self.k
    def lead(self):
        if not self.k: return None
        return max(self.k, key=lambda s: SYM[s]['rank'])
    def sign(self):
        s = self.lead()
        if s is None: return (self.c > 0) - (self.c < 0)
        return 1 if self.k[s] > 0 else -1
    def val(self, inst): return self.c + sum(v * inst[s] for s, v in self.k.items())
    def __repr__(self):
        parts = []
        for s in sorted(self.k, key=lambda s: -SYM[s]['rank']):
            v = self.k[s]; parts.append(('%s' % s) if v == 1 else ('%s*%s' % (v, s)))
        if self.c or not parts: parts.append(str(self.c))
        return '+'.join(parts).replace('+-', '-')
def cmp(a, b): return (a - b).sign()
SYM = {}
def newsym(origin):
    name = 'S%d' % (len(SYM) + 1); SYM[name] = {'rank': len(SYM), 'res': 40, 'origin': origin}; return name
# ---------------------------------------------------------------- config helpers
def norm(items):
    out = []
    for it in items:
        kind, v = it
        if kind == 't' and v.isc() and v.c == 1: kind, v = 'r', Aff(1)
        if kind == 'r':
            if v.isc() and v.c == 0: continue
            if out and out[-1][0] == 'r': out[-1] = ('r', out[-1][1] + v); continue
        out.append((kind, v))
    return out
def show(items, A, maxi=None):
    s = []
    for kind, v in items[-(maxi or len(items)):]:
        s.append(('1^(%s)' % v) if kind == 'r' and not v.isc() else ('1^%s' % v) if kind == 'r' else str(v))
    pre = '... ' if maxi and len(items) > maxi else ''
    return '[%s%s | %s]' % (pre, ' '.join(s), A)
# ---------------------------------------------------------------- instantiation of a window
def instantiate(affs):
    """numeric values for all symbols in affs: leading symbols spaced by --gap, others small; residues = SYM res mod MOD.
    returns dict sym -> int"""
    syms = set()
    for a in affs: syms |= set(a.k)
    order = sorted(syms, key=lambda s: SYM[s]['rank'])
    inst = {}; cur = args.base
    for s in order:
        # value grows by gap per rank
        cur = cur * args.gap
        v = cur - (cur % MOD) + (SYM[s]['res'] % MOD)
        inst[s] = v
    return inst
def window_numeric(items, A, inst):
    nums = []
    for kind, v in items: nums.append(v.val(inst))
    return nums, A.val(inst)
# ---------------------------------------------------------------- event learning
CACHE = {}
def run_event_numeric(prefix_items_num, A_num):
    # prefix_items_num: list of (kind, int)
    ts = []
    for kind, v in prefix_items_num:
        v = int(v)
        if kind == 'r': ts += [1] * v
        else: ts.append(v)
    r = probe.ev(ts, int(A_num), args.tm, args.maxseg)
    return r
def tokens_to_items(ts):
    out = []
    for x in ts:
        if x == 1:
            if out and out[-1][0] == 'r': out[-1] = ('r', out[-1][1] + 1)
            else: out.append(('r', 1))
        else: out.append(('t', x))
    return out
DUMMY = [('t', 5), ('t', 2), ('t', 0), ('t', 7), ('t', 2), ('t', 0)]
def sigkey(items, A, K):
    win = items[-K:]; affs = [v for _, v in win] + [A]
    inst = instantiate(affs)
    leads = sorted({a.lead() for a in affs if not a.isc()}, key=lambda s: SYM[s]['rank'])
    pos = {s: i for i, s in enumerate(leads)}
    key = [K, K == len(items)]
    for (kind, a) in list(win) + [('A', A)]:
        if a.isc(): key.append((kind, 'c', a.c)); continue
        terms = sorted(a.k.items(), key=lambda t: -SYM[t[0]]['rank'])
        sig = tuple((pos.get(sy, -1), cf) for sy, cf in terms[:2])
        key.append((kind, 'v', int(a.val(inst)) % MOD, sig))
    return tuple(key)
def apply_rule(rule, items, A, K):
    kinds, out0, coefs, base, A0, Acoef = rule
    affs = [v for _, v in items[-K:]] + [A]
    outs = []
    for j, kind in enumerate(kinds):
        a = Aff(out0[j])
        for i, ci in enumerate(coefs):
            if ci is not None and ci[j]: a = a + (affs[i] - base[i]) * ci[j]
        outs.append((kind, a))
    nA = Aff(A0)
    for i, ci in enumerate(Acoef):
        if ci: nA = nA + (affs[i] - base[i]) * ci
    return outs, nA
def learn(items, A, K):
    """learn the event on the last K items (+A). Returns (n_consumed, out_items_affine, newA) or a string."""
    win = items[-K:]; affs = [v for _, v in win] + [A]
    inst = instantiate(affs)
    base = [v.val(inst) for v in affs]
    if any(x != int(x) or x < 0 for x in base): return 'BADINST %s' % base
    dum = DUMMY if K < len(items) else []
    def runwith(vals):
        pre = dum + [(win[i][0], vals[i]) for i in range(len(win))]
        return run_event_numeric(pre, vals[-1])
    r0 = runwith(base); ctx0 = probe.LAST_CTX
    if isinstance(r0, str): return 'EVENT-NONB ' + r0
    out0 = tokens_to_items(r0[0]); A0 = r0[1]
    # dummy prefix intact?
    if out0[:len(dum)] != dum: return 'WIDEN'
    out0 = out0[len(dum):]
    # perturb each input
    coefs = []
    for i in range(len(base)):
        if win[i][1].isc() if i < len(win) else A.isc():
            coefs.append(None); continue
        vals = list(base); vals[i] += MOD
        r = runwith(vals)
        if isinstance(r, str): return 'PERTURB-NONB %d %s' % (i, r)
        o = tokens_to_items(r[0])
        if o[:len(dum)] != dum: return 'WIDEN'
        o = o[len(dum):]
        if [k for k, _ in o] != [k for k, _ in out0]: return 'SHAPE-CHANGE at input %d: %s vs %s' % (i, o, out0)
        coefs.append(([Fr(o[j][1] - out0[j][1], MOD) for j in range(len(o))], Fr(r[1] - A0, MOD)))
    # build affine outputs: out = out0 + sum coef_i * (input_i - base_i)
    outs = []
    for j, (kind, v0) in enumerate(out0):
        a = Aff(v0)
        for i in range(len(base)):
            if coefs[i] is None: continue
            ci = coefs[i][0][j]
            if ci: a = a + (affs[i] - base[i]) * ci
        outs.append((kind, a))
    nA = Aff(A0)
    for i in range(len(base)):
        if coefs[i] is None: continue
        ci = coefs[i][1]
        if ci: nA = nA + (affs[i] - base[i]) * ci
    # verification: perturb all inputs at once by 2*MOD and compare
    vals = [b + (2 * MOD if (i < len(win) and not win[i][1].isc()) or (i == len(win) and not A.isc()) else 0) for i, b in enumerate(base)]
    inst2 = None
    r = runwith(vals)
    if isinstance(r, str): return 'VERIFY-NONB ' + r
    o = tokens_to_items(r[0])[len(dum):]
    pred = []
    for kind, a in outs:
        # numeric prediction: evaluate a with inputs shifted: since a is affine in affs, shift = sum coef*2MOD
        pv = a.val(inst)
        for i in range(len(base)):
            if coefs[i] is None: continue
            ci = coefs[i][0][len(pred)]
            pv += ci * (vals[i] - base[i])
        pred.append((kind, pv))
    if [(k, int(v)) for k, v in pred] != [(k, v) for k, v in o]: return 'VERIFY-FAIL pred %s got %s' % (pred, o)
    rule = ([k for k, _ in out0], [v for _, v in out0], [None if c is None else c[0] for c in coefs], base, A0, [0 if c is None else c[1] for c in coefs])
    return (K, outs, nA, '%d steps %s' % (r0[2], ctx0), rule)
# ---------------------------------------------------------------- main loop
def clr(items, A):
    """apply CLR if possible; returns (items, A, info) or None"""
    n = Aff(0); i = len(items) - 1
    while i >= 0 and items[i][0] == 'r': n = n + items[i][1]; i -= 1
    if i < 0: return None
    x = items[i][1]
    if cmp(x, Aff(3)) < 0: return None
    inst = instantiate([x])
    c = int(x.val(inst)) % 3
    d = (x - c) * Fr(1, 3)
    new = list(items); new[i] = ('t', Aff(c))
    if n.isc() and n.c == 0 and d.isc() and d.c <= 6:
        nA = A
        for _ in range(int(d.c)): nA = nA * 2 + 8          # R1 exact
        info = 'R1x%d' % d.c
    elif n.isc() and A.isc() and d.isc() and n.c <= 1 and A.c < 50 and d.c <= 3:
        v = int(A.c)
        for _ in range(int(d.c)):
            v = 2 * v + 8 if n.c == 0 else Uexact(int(n.c), v)
        nA = Aff(v); info = 'exact'
    else:
        s = newsym('U_{%s}^{%s}(%s)' % (n, d, A)); nA = Aff(0, {s: 1}); info = 'new %s' % s
        if n.isc() and n.c < 2: SYM[s]['res'] = 40  # (n<2 residue not tracked exactly)
    return norm(new), nA, info
def Uexact(j, a):
    if j == 0: return 2 * a + 8
    v = 4
    for _ in range(a // 3 + 1): v = Uexact(j - 1, v)
    return v
items = norm([('t', Aff(7))] + [('r', Aff(35))]); A = Aff(4)
nev = 0; log = []
while nev < args.events:
    r = clr(items, A)
    if r:
        items, A, info = r; continue
    # event: learn on a window
    K = min(args.win, len(items)); cached = False
    while True:
        key = sigkey(items, A, K)
        if key in CACHE:
            if CACHE[key] == 'WIDEN': K = min(len(items), K + 3); continue
            outs, nA = apply_rule(CACHE[key], items, A, K); res = (K, outs, nA, 0, None); cached = True; break
        res = learn(items, A, K)
        if res == 'WIDEN' and K < len(items): CACHE[key] = 'WIDEN'; K = min(len(items), K + 3); continue
        if not isinstance(res, str): CACHE[key] = res[4]
        break
    nev += 1
    if isinstance(res, str):
        print('EV%d STOPPED: %s\n   at %s' % (nev, res, show(items, A, args.show))); break
    K, outs, nA, steps = res[:4]
    before = show(items, A, args.show)
    items = norm(items[:-K] + outs); A = nA
    print('EV%d %s -> %s  (win %d, %s)' % (nev, before, show(items, A, args.show), K, 'cached' if cached else steps), flush=True)
print('symbols:'); [print(' ', s, d['origin']) for s, d in SYM.items()]
