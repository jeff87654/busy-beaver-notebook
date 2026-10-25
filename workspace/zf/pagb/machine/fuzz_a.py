"""Semantic soundness fuzz for design A: every AX root (rows and the gated bundle), at random and at
forced-colliding parameters, is decoded and evaluated in the standard model ℕ.

Decoding (design A): D(0)=⊤; D(4P(x,y)+0)=D x→D y; +1: σT(x)==T(y); +2: ∀v_x D y; +3: T(x)==T(y).
T(0)=0; T(4P(j,k)+0)=σT(j); +1: T(j)⊕T(k); +2: T(j)⊗T(k); +3: v_j.   (F = D(1) = σ0==0.)
A root is (AST with parameters); its decoded formula = the AST with formula-position parameters
replaced by D(value) and term-position parameters by T(value).  check_decoder() confirms this equals
D(code) wherever the code is small enough to decode exactly.

Quantifiers are bounded: ∀v ranges over 0..K (∃ = ¬∀¬, so witnesses are also ≤ K). Free variables get
random values in 0..VMAX per trial. A FALSE verdict at K is re-checked at a larger K2; one that
persists is reported. NG is excluded (its truth is ¬Goldbach). Gate-closed AX leaves ⊤ current.
Usage: python fuzz_a.py [n_param_samples] [trials_per_sample]
"""
import sys, os, random, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('PA_DESIGN', 'A')
import design, spec_pa as spec
from bignum import unP

# ---- semantic trees: ('top',) ('imp',A,B) ('all',i,A) ('at',s,t);  terms ('z',) ('s',t) ('+',t,u) ('*',t,u) ('v',i)
def T(n):
    if n == 0: return ('z',)
    q, t = divmod(n, 4); j, k = unP(q)
    if t == 0: return ('s', T(j))
    if t == 1: return ('+', T(j), T(k))
    if t == 2: return ('*', T(j), T(k))
    return ('v', j)

def D(n):
    if n == 0: return ('top',)
    q, t = divmod(n, 4); x, y = unP(q)
    if t == 0: return ('imp', D(x), D(y))
    if t == 1: return ('at', ('s', T(x)), T(y))
    if t == 2: return ('all', x, D(y))
    return ('at', T(x), T(y))

FF = D(1)
def NOT(a): return ('imp', a, FF)

def val(x, env):
    if x == 'd': return env['c'] + 1
    if x == 'e': return env['c'] + 2
    if x in ('phi',): return env['c']
    if x.isdigit(): return int(x)
    return env[x]

def sem_term(t, env):
    if isinstance(t, str):
        if t == 'Z0': return ('z',)
        return T(val(t, env))                       # raw parameter used as a term code
    h = t[0]
    if h == 'V': return ('v', val(t[1], env))
    if h == 'S1': return ('s', sem_term(t[1], env))
    if h == 'add': return ('+', sem_term(t[1], env), sem_term(t[2], env))
    if h == 'mul': return ('*', sem_term(t[1], env), sem_term(t[2], env))
    raise ValueError(t)

def sem(f, env):
    if isinstance(f, str):
        if f == 'F': return FF
        return D(val(f, env))                      # formula-position parameter
    h = f[0]
    if h == 'teq': return ('at', sem_term(f[1], env), sem_term(f[2], env))
    if h == 'srel': return ('at', ('s', sem_term(f[1], env)), sem_term(f[2], env))
    if h == 'im': return ('imp', sem(f[1], env), sem(f[2], env))
    if h == 'all': return ('all', val(f[1], env), sem(f[2], env))
    if h == 'not': return NOT(sem(f[1], env))
    if h == 'and': return NOT(('imp', sem(f[1], env), NOT(sem(f[2], env))))
    if h == 'ex': return NOT(('all', val(f[1], env), NOT(sem(f[2], env))))
    if h == 'or': return ('imp', NOT(sem(f[1], env)), sem(f[2], env))
    raise ValueError(f)

def tv(t, rho):
    h = t[0]
    if h == 'z': return 0
    if h == 'v': return rho(t[1])
    if h == 's': return tv(t[1], rho) + 1
    if h == '+': return tv(t[1], rho) + tv(t[2], rho)
    return tv(t[1], rho) * tv(t[2], rho)

def ev(f, rho, K):
    h = f[0]
    if h == 'top': return True
    if h == 'at': return tv(f[1], rho) == tv(f[2], rho)
    if h == 'imp': return (not ev(f[1], rho, K)) or ev(f[2], rho, K)
    i, A = f[1], f[2]
    for x in range(K + 1):
        r2 = (lambda i, x, rho: (lambda j: x if j == i else rho(j)))(i, x, rho)
        if not ev(A, r2, K): return False
    return True

def size(f):
    return 1 if f[0] in ('top', 'at') else 1 + sum(size(g) for g in f[1:] if isinstance(g, tuple))

def qdepth(f):
    if f[0] in ('top', 'at'): return 0
    if f[0] == 'all': return 1 + qdepth(f[2])
    return max(qdepth(f[1]), qdepth(f[2]))

def tau(f):
    """identify Imp(⊤,⊤) with ⊤ (the code-level collapse wim(0,0) = 0; semantically equivalent)."""
    if f[0] == 'imp':
        a, b = tau(f[1]), tau(f[2])
        return ('top',) if a == ('top',) and b == ('top',) else ('imp', a, b)
    if f[0] == 'all': return ('all', f[1], tau(f[2]))
    return f

def check_decoder(rnd, n=300):
    """AST-substitution decoding == D(code) when the code is exactly representable."""
    bad = ok = 0
    roots = [('row', r) for r in design.PRE + list(design.ROWS)] + [('bundle', design.BUNDLE)]
    for _ in range(n):
        env = {k: rnd.randint(0, 4) for k in 'abchu'}
        for kind, r in roots:
            e = dict(env);
            code = spec.ev(r, e)
            if not isinstance(code, int): continue
            ok += 1
            if tau(D(code)) != tau(sem(r, e)): bad += 1
    return ok, bad

def main(nsamp=400, ntr=30, K=6, K2=14, VMAX=4, seed=11):
    rnd = random.Random(seed)
    ok, bad = check_decoder(rnd)
    print(f'decoder cross-check: {ok} exact codes, {bad} mismatches')
    roots = [(f'row{j+1}', r, 'post') for j, r in enumerate(design.ROWS)
                                               if j != design.NG_INDEX]
    false = []; nchk = 0; skipped = 0; closed = 0
    for s in range(nsamp):
        k = rnd.random()
        env = {'a': rnd.randint(0, 9), 'b': rnd.randint(0, 9), 'c': rnd.randint(0, 40), 'u': rnd.randint(0, 40),
               'h': rnd.randint(0, 40)}
        # forced collisions
        if k < 0.15: env['b'] = env['a']
        elif k < 0.25: env['a'] = env['c'] + 1
        elif k < 0.35: env['b'] = env['c'] + 1
        elif k < 0.45: env[rnd.choice('abc')] = 0
        elif k < 0.55: env['c'] = rnd.choice([env['a'], env['b']])       # gate-closed
        elif k < 0.62: env['u'] = rnd.choice([env['a'], env['b'], env['c'] + 1, 0])   # u collisions
        elif k < 0.67: env['c'] = env['u']                                 # gate-closed via u
        if getattr(design, 'GATE', '') == 'occ' and rnd.random() < 0.5:
            # (a): a, b as genuine term codes, sometimes containing v_c (gate closes), sometimes not
            def rt(dep):
                k = rnd.random()
                if dep == 0 or k < 0.35:
                    return spec.weq(env['c'] if rnd.random() < 0.3 else rnd.randint(0, 6), 0)
                if k < 0.45: return 0
                if k < 0.65: return spec.wim(rt(dep - 1), 1)
                return rnd.choice([spec.wel, spec.wal])(rt(dep - 1), rt(dep - 1))
            env['a'] = rt(2); env['b'] = rt(2)
        items = list(roots)
        gate_open = spec.gate_open(env['a'], env['b'], env['c'], env['u'])
        items.append(('BUNDLE' if gate_open else 'BUNDLE(gate closed -> ⊤)', design.BUNDLE, 'bundle'))
        for name, r, where in items:
            if where == 'bundle' and not gate_open:
                closed += 1; continue               # spec: current := 0 = ⊤
            f = sem(r, env)
            if size(f) > 400 or qdepth(f) > 7:
                skipped += 1; continue
            KK = K if qdepth(f) <= 4 else 3
            for _ in range(ntr):
                vals = {}
                rho = lambda j: vals.setdefault(j, rnd.randint(0, VMAX))
                nchk += 1
                if not ev(f, rho, KK):
                    fixed = dict(vals)
                    rho2 = lambda j: fixed.setdefault(j, 0)
                    if not ev(f, rho2, K2 if qdepth(f) <= 3 else KK + 2):
                        false.append((name, dict(env), fixed)); break
    print(f'evaluations: {nchk}; skipped (too large) {skipped}; gate-closed bundle cases {closed} (current = ⊤)')
    print(f'FALSE instances: {len(false)}')
    for x in false[:20]:
        print('  ', x)
    return len(false) + bad

if __name__ == '__main__':
    a = [int(x) for x in sys.argv[1:]]
    raise SystemExit(1 if main(*a) else 0)

def sensitivity(seed=5, nsamp=200, ntr=25):
    """the fuzz must flag known-unsound formulas: mutants, and the bundle with the gate ignored."""
    import search_a as A
    from pagen import im, al, ex
    rnd = random.Random(seed)
    V, S1, teq = A.V, A.S1, A.teq
    mutants = {
        'vacuity on its own variable  v_a==v_b -> ∀a v_a==v_b': im(teq(V('a'), V('b')), al('a', teq(V('a'), V('b')))),
        'existence with occurring var ∃a v_a==σv_a': ex('a', teq(V('a'), S1(V('a')))),
        'wrong add_rec  σx⊕y == x⊕σσy': teq(A.add(S1(V('a')), V('b')), A.add(V('a'), S1(S1(V('b'))))),
        'IND without the base case': im(al('a', im('phi', al('c', im(teq(V('c'), S1(V('a'))), al('a', im(teq(V('a'), V('c')), 'phi')))))), al('a', 'phi')),
        'BUNDLE with gate ignored (c = a)': design.BUNDLE,
    }
    out = {}
    for name, r in mutants.items():
        hits = 0
        for _ in range(nsamp):
            env = {'a': rnd.randint(0, 9), 'b': rnd.randint(0, 9), 'c': rnd.randint(0, 40), 'u': 0, 'h': 0}
            if 'gate ignored' in name:
                if getattr(design, 'GATE', '') == 'occ':
                    env['a'] = spec.weq(env['c'], 0)          # T(a) = v_c: c occurs, gate would close
                else:
                    env['c'] = rnd.choice([env['a'], env['b']])
            f = sem(r, env)
            if qdepth(f) > 7: continue
            for _ in range(ntr):
                vals = {}
                rho = lambda j: vals.setdefault(j, rnd.randint(0, 4))
                if not ev(f, rho, 6): hits += 1; break
        out[name] = hits
        print(f'  {name}: flagged false in {hits}/{nsamp} parameter samples')
    return out

if __name__ == '__main__' and os.environ.get('FUZZ_SENS'):
    sensitivity()
