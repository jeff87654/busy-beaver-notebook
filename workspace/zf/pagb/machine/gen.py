"""Generate variants of the zfc_254 source with a replaced AX bundle, compile them with Wade's
TMBuilder and report state counts.

A bundle is a named formula AST:
    ('el', x, y)  x∈y        ('eq', x, y)  x=y       ('im', A, B)    ('all', x, A)
    ('ex', x, A)  (wex)      ('and', A, B) (wa)      ('not', A) (wn) 'phi' (the code c itself)
Variables: 'a' = param1, 'b' = param2 (after the read), 'c' = param3, plus derived labels in PUSH.

Usage: python gen.py [variant ...]      (no argument: all variants)
Writes source_<variant>.py next to this file (the build/validation tools take the variant name).
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'ext', 'turing_machine_explorer'))
sys.path.insert(0, HERE)

SRC = os.path.join(HERE, 'source_local.py')

def split_items(body):
    items = []; depth = 0; cur = ''
    for ch in body:
        if ch in '([': depth += 1
        if ch in ')]': depth -= 1
        if ch == ',' and depth == 0:
            items.append(cur.strip()); cur = ''
        else:
            cur += ch
    items.append(cur.strip())
    return items

def load_axioms_items():
    src = open(SRC, encoding='utf-8').read()
    i = src.index('    def axioms(self):')
    j = src.index('return [', i)
    k = src.index('\n', j)
    return src, j, k, split_items(src[j + 8:k - 1])

BUNDLE_START, GATE_START = 89, 182      # item indices in source_local.axioms() (checked in main)

PUSH = {'a': ['par1'], 'b': ['par2'], 'c': ['par3'], 'phi': ['par3'],
        'd': ['par3', 'self.topwff.inc'],                       # c+1
        'e': ['par1', 'par2', 'wel', 'par3', 'wel']}            # Rel(Rel(a,b),c) > a, b, c

def rpn(f):
    if isinstance(f, str):
        return list(PUSH[f])
    h = f[0]
    if h == 'el': return rpn(f[1]) + rpn(f[2]) + ['wel']
    if h == 'eq': return rpn(f[1]) + rpn(f[2]) + ['weq']
    if h == 'im': return rpn(f[1]) + rpn(f[2]) + ['wim']
    if h == 'all': return rpn(f[1]) + rpn(f[2]) + ['wal']
    if h == 'ex': return rpn(f[1]) + rpn(f[2]) + ['wex']
    if h == 'and': return rpn(f[1]) + rpn(f[2]) + ['wa']
    if h == 'not': return rpn(f[1]) + ['wn']
    raise ValueError(f)

# ---- formula helpers
def el(x, y): return ('el', x, y)
def eq(x, y): return ('eq', x, y)
def im(a, b): return ('im', a, b)
def al(x, a): return ('all', x, a)
def ex(x, a): return ('ex', x, a)
def an(a, b): return ('and', a, b)
def ands(*xs):                      # right-nested
    return xs[0] if len(xs) == 1 else an(xs[0], ands(*xs[1:]))
def sub(x, y, u): return al(u, im(el(u, x), el(u, y)))        # x ⊆ y via element variable u
PHI = 'phi'

def V(a='a', b='b', c='c'):
    return an(im(el(a, b), al(c, el(a, b))), im(eq(a, b), al(c, eq(a, b))))

# ---- the original bundle (must reproduce source_local exactly)
def orig():
    pow_ = ex('c', an(al('b', im(sub('b', 'a', 'c'), el('b', 'c'))), el('c', 'b')))
    tr = sub('a', 'b', 'c')
    C = ex('b', an(al('a', im(el('a', 'b'), an(pow_, tr))), el('c', 'b')))
    w = ex('b', an(PHI, el('b', 'c')))
    G = ex('c', an(al('a', im(el('a', 'b'), al('b', im(PHI, w)))), al('b', im(el('b', 'c'), ex('a', PHI)))))
    return an(an(C, G), V())

VARIANTS = {'orig': (orig, None)}

# ---- candidate bundles ------------------------------------------------------------------------
def cl1(C):            # ∀a∈B ∀y (φ(a,y) → ∃y' (φ(a,y') ∧ y'∈C)),  B = b (shadowed by the output)
    return al('a', im(el('a', 'b'), al('b', im(PHI, ex('b', an(PHI, el('b', C)))))))
def cl2(C):            # ∀y∈C ∃x φ(x,y)
    return al('b', im(el('b', C), ex('a', PHI)))

def ug1():
    """UG with clause 3 := (C ⊆ w → C ∈ w);  w = a, x = B = b, W = C = c, p = c (free)."""
    X = an(sub('b', 'a', 'c'), ex('c', an(al('a', im(sub('a', 'b', 'c'), el('a', 'c'))), el('c', 'a'))))
    Y = ex('c', ands(cl1('c'), cl2('c'), im(sub('c', 'a', 'b'), el('c', 'a'))))
    return ex('a', an(el('c', 'a'), al('b', im(el('b', 'a'), an(X, Y)))))
VARIANTS['ug1'] = (lambda: an(ug1(), V()), None)

def ug0(D='d', p='a'):
    """interface UG;  w = c, x = B = b, W = a, C = D (fresh: c+1 or a code > a,b,c), p free."""
    X = an(sub('b', 'c', 'a'), ex('a', an(al('c', im(sub('c', 'b', 'a'), el('c', 'a'))), el('a', 'c'))))
    H = al('a', im(el('a', 'b'), ex('b', an(el('b', 'c'), PHI))))
    Y = ex(D, ands(cl1(D), cl2(D), im(H, el(D, 'c'))))
    return ex('c', an(el(p, 'c'), al('b', im(el('b', 'c'), an(X, Y)))))
VARIANTS['ug0e'] = (lambda: an(ug0('e'), V()), None)          # collision-free fresh label
VARIANTS['ug0d_nogate'] = (lambda: an(ug0('d'), V()), None)   # c+1, cost only (gate NOT extended)

def ug_sep():
    """old C ∧ G' kept, plus a separate universe clause U (clause 3 in the C ⊆ w form)."""
    CG = orig()[1]
    U = ex('a', an(el('c', 'a'), al('b', im(el('b', 'a'), an(
        an(sub('b', 'a', 'c'), ex('c', an(al('a', im(sub('a', 'b', 'c'), el('a', 'c'))), el('c', 'a')))),
        ex('c', ands(cl1('c'), cl2('c'), im(sub('c', 'a', 'b'), el('c', 'a')))))))))
    return an(an(CG, U), V())
VARIANTS['sep'] = (ug_sep, None)

def tg():
    """CHOSEN (search.py ug0dz optimum, 288 states).  w = d = c+1, C = W = c, x = B = b, z = d, p = c;
    the label a occurs only as the φ input."""
    cl1 = al('a', im(el('a', 'b'), al('b', im(PHI, ex('b', an(el('b', 'c'), PHI))))))
    cl3 = im(al('a', im(el('a', 'b'), ex('b', an(el('b', 'd'), PHI)))), el('c', 'd'))
    cl2 = al('b', im(el('b', 'c'), ex('a', PHI)))
    Y = ex('c', an(cl1, an(cl3, cl2)))
    Q = ex('c', an(al('d', im(sub('d', 'b', 'c'), el('d', 'c'))), el('c', 'd')))
    T = sub('b', 'd', 'c')
    UG = ex('d', an(al('b', im(el('b', 'd'), an(Y, an(Q, T)))), el('c', 'd')))
    Vf = V()
    return an(UG, an(Vf[2], Vf[1]))
VARIANTS['superseded_ug288'] = (tg, None)   # SUPERSEDED (UG, interface before 2026-10-14 change)

PUSH['0'] = ['v_0']                      # label 0 (the f variable of UG')
def tgp():
    """CHOSEN for UG' (search2.py A optimum, 296 states).  As tg plus: ∀0 (f) between ∃w and ∀x∈w;
    clause 3 concludes ∃U∈w ∀y∈C ∀z∈y z∈U with U = b, y = d, z = c."""
    cl1 = al('a', im(el('a', 'b'), al('b', im(PHI, ex('b', an(el('b', 'c'), PHI))))))
    cl2 = al('b', im(el('b', 'c'), ex('a', PHI)))
    U = ex('b', an(el('b', 'd'), al('d', im(el('d', 'c'), sub('d', 'b', 'c')))))
    cl3 = im(al('a', im(el('a', 'b'), ex('b', an(el('b', 'd'), PHI)))), U)
    Y = ex('c', an(an(cl2, cl3), cl1))
    Q = ex('c', an(al('d', im(sub('d', 'b', 'c'), el('d', 'c'))), el('c', 'd')))
    T = sub('b', 'd', 'c')
    UG = ex('d', an(al('0', al('b', im(el('b', 'd'), an(Y, an(T, Q))))), el('c', 'd')))
    Vf = V()
    return an(UG, an(Vf[2], Vf[1]))
VARIANTS['tg'] = (tgp, None)

def gen_source(name, fn=None, gate=None):
    if fn is None:
        fn, gate = VARIANTS[name]
    src, j, k, items = load_axioms_items()
    assert items[GATE_START].startswith('self.while_decnz(self.param3'), items[GATE_START]
    btoks = rpn(fn())
    gate_items = items[GATE_START:] if gate is None else gate
    new = items[:BUNDLE_START] + btoks + gate_items
    out = src[:j + 8] + ', '.join(new) + src[k - 1:]
    path = os.path.join(HERE, f'source_{name}.py')
    open(path, 'w', encoding='utf-8').write(out)
    return path, len(btoks)

def compile_variant(name, save=False):
    import importlib
    mod = importlib.import_module(f'source_{name}')
    importlib.reload(mod)
    z = mod.ZF2(); z.debug = False
    z.build_machine()
    if save:
        z.tm.save(os.path.join(HERE, f'm254tg_{name}.tm'))
    return z, len(set(s[0] for s in z.tm.states))

if __name__ == '__main__':
    src, j, k, items = load_axioms_items()
    assert rpn(orig()) == items[BUNDLE_START:GATE_START], 'orig bundle does not reproduce the source'
    names = sys.argv[1:] or list(VARIANTS)
    for n in names:
        path, nt = gen_source(n)
        z, ns = compile_variant(n)
        print(f'{n:12s} bundle tokens {nt:4d}  states {ns}')
