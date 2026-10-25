"""Independent re-check of the collapsed-matrix countermodels.  The ZF axiom formulas are parsed from
zf/v354/coq/Logic.v itself (not re-typed), and the logical schemes are written from Logic.v's prov."""
import re, sys
src = open('../../v354/coq/Logic.v').read()
def grab(name):
    m = re.search(r'Definition %s[^:]*:\s*wff\s*:=(.*?)\.\n' % name, src, re.S); return m.group(1)
def tok(s): return re.findall(r'\(|\)|[A-Za-z_0-9]+', s)
def parse(ts, i):
    t = ts[i]
    if t == '(':
        f, i = parse(ts, i + 1); assert ts[i] == ')'; return f, i + 1
    ar = {'Weq': 2, 'Wel': 2, 'Wim': 2, 'Wn': 1, 'Wal': 2, 'Wex': 2, 'Wa': 2}
    if t in ar:
        args = []; i += 1
        for _ in range(ar[t]):
            a, i = parse(ts, i); args.append(a)
        return (t, *args), i
    return t, i + 1
def P(name):
    f, i = parse(tok(grab(name)), 0); return f
ZF = {k: P(k) for k in ('EXT', 'POW', 'UNI', 'INF')}
m = re.search(r'Definition REP \(ph : wff\) : wff :=(.*?)\.\n', src, re.S)
REPf, _ = parse(tok(m.group(1)), 0)

def ev(f, I, N, Q, eq, el, ph=None):
    r = lambda g: ev(g, I, N, Q, eq, el, ph)
    if isinstance(f, str): return ph if f == 'ph' else None
    h = f[0]
    if h == 'Weq': return eq
    if h == 'Wel': return el
    if h == 'Wim': return I[r(f[1])][r(f[2])]
    if h == 'Wn': return N[r(f[1])]
    if h == 'Wal': return Q[r(f[2])]
    if h == 'Wex': return N[Q[N[r(f[2])]]]
    if h == 'Wa': return N[I[r(f[1])][N[r(f[2])]]]

def check(name, I, N, Q, eq, el, D):
    nv = len(N); V = range(nv)
    imp = lambda a, b: I[a][b]; neg = lambda a: N[a]; al = lambda a: Q[a]
    ex = lambda a: neg(al(neg(a))); wa = lambda a, b: neg(imp(a, neg(b)))
    # subalgebra
    S = {eq, el}
    while True:
        T = S | {N[a] for a in S} | {Q[a] for a in S} | {I[a][b] for a in S for b in S}
        if T == S: break
        S = T
    res = {}
    res['DET'] = all(not (a in D and imp(a, b) in D) or b in D for a in S for b in S)
    res['GEN'] = all(a not in D or al(a) in D for a in S)
    res['B1'] = all(imp(imp(a, b), imp(imp(b, c), imp(a, c))) in D for a in S for b in S for c in S)
    res['B2'] = all(imp(imp(neg(a), a), a) in D for a in S)
    res['B3'] = all(imp(a, imp(neg(a), b)) in D for a in S for b in S)
    res['B4'] = all(imp(al(imp(a, b)), imp(al(a), al(b))) in D for a in S for b in S)
    res['B6a'] = wa(imp(eq, al(eq)), imp(el, al(el))) in D
    res['B6b'] = all(imp(al(al(a)), al(al(a))) in D for a in S)
    res['B6c'] = all(imp(ex(al(a)), a) in D for a in S)
    res['B7'] = ex(eq) in D
    res['B8a'] = imp(eq, imp(eq, eq)) in D
    res['B8b'] = imp(eq, imp(el, el)) in D
    res['B8c'] = imp(eq, imp(el, el)) in D
    for k, f in ZF.items(): res[k] = ev(f, I, N, Q, eq, el) in D
    res['REP'] = all(ev(REPf, I, N, Q, eq, el, a) in D for a in S)
    bad = [k for k, v in res.items() if not v]
    print(name, 'S =', sorted(S), 'violated:', bad)

check('B1', [(0,1,1),(0,0,2),(0,0,0)], (2,0,1), (0,1,1), 0, 0, {0})
check('B2', [(0,1,1),(0,0,0),(0,0,0)], (2,0,1), (0,1,1), 0, 0, {0})
check('B3', [(0,0,2),(0,0,2),(0,0,0)], (0,2,0), (0,0,1), 0, 1, {0,1})
