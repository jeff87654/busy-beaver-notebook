"""Closed-sentence DSL for the m254gb bundle conjunct NG' (role-named formulas, label assignment,
RPN generation, compilation with Wade's TMBuilder).

A formula is a nested tuple over *roles* (unique binder names):
    ('el', x, y) x∈y   ('eq', x, y) x=y   ('im', A, B)   ('and', A, B)   ('or', A, B) = ¬A→B
    ('not', A)         ('all', x, A)      ('ex', x, A)    FALSUM (falsity, code 1)
Roles are mapped to constant variable labels 0..9 (never the AX parameters a, b, c), so NG' is a
fixed closed sentence and the gate / collision analysis of the base bundle is untouched.
"""
import os, sys, itertools, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen

FALSUM = '<F>'          # falsity constant (code 1); never a role name
LABEL_TOK = {0: ['v_0'], 1: ['v_1'], 2: ['v_2'], 3: ['v_3'], 4: ['self.v_4()'], 5: ['load_5']}
for k in range(6, 12):
    LABEL_TOK[k] = ['load_5'] + ['self.topwff.inc'] * (k - 5)

# ---- constructors
def el(x, y): return ('el', x, y)
def eq(x, y): return ('eq', x, y)
def im(a, b): return ('im', a, b)
def an(a, b): return ('and', a, b)
def orr(a, b): return ('or', a, b)
def no(a): return ('not', a)
def al(x, a): return ('all', x, a)
def ex(x, a): return ('ex', x, a)
def ands(*xs): return xs[0] if len(xs) == 1 else an(xs[0], ands(*xs[1:]))
def ors(*xs): return xs[0] if len(xs) == 1 else orr(xs[0], ors(*xs[1:]))
def ball(x, s, a): return al(x, im(el(x, s), a))          # ∀x∈s A
def bex(x, s, a): return ex(x, an(el(x, s), a))           # ∃x∈s A
def sub(u, x, y): return ball(u, x, el(u, y))             # x ⊆ y (element role u)

# ---- RPN
def rpn(f, lab):
    if isinstance(f, str):
        if f == FALSUM: return ['v_1']
        return list(LABEL_TOK[lab[f]])
    h = f[0]
    if h == 'el': return rpn(f[1], lab) + rpn(f[2], lab) + ['wel']
    if h == 'eq': return rpn(f[1], lab) + rpn(f[2], lab) + ['weq']
    if h == 'im': return rpn(f[1], lab) + rpn(f[2], lab) + ['wim']
    if h == 'and': return rpn(f[1], lab) + rpn(f[2], lab) + ['wa']
    if h == 'or': return rpn(f[1], lab) + ['wn'] + rpn(f[2], lab) + ['wim']
    if h == 'not': return rpn(f[1], lab) + ['wn']
    if h == 'all': return rpn(f[1], lab) + rpn(f[2], lab) + ['wal']
    if h == 'ex': return rpn(f[1], lab) + rpn(f[2], lab) + ['wex']
    raise ValueError(f)

def roles(f, acc=None):
    acc = [] if acc is None else acc
    if isinstance(f, str): return acc
    if f[0] in ('all', 'ex'):
        if f[1] not in acc: acc.append(f[1])
        roles(f[2], acc)
    elif f[0] in ('im', 'and', 'or'):
        roles(f[1], acc); roles(f[2], acc)
    elif f[0] == 'not':
        roles(f[1], acc)
    return acc

def check(f, lab, env=()):
    """every role occurrence resolves to its own binder (no capture), and the formula is closed."""
    if isinstance(f, str) and f != FALSUM: raise ValueError('bare role as formula: ' + f)
    def look(l):
        for (k, r) in reversed(env):
            if k == l: return r
        return None
    if isinstance(f, str): return True
    h = f[0]
    if h in ('all', 'ex'): return check(f[2], lab, env + ((lab[f[1]], f[1]),))
    if h in ('im', 'and', 'or'): return check(f[1], lab, env) and check(f[2], lab, env)
    if h == 'not': return check(f[1], lab, env)
    if h in ('el', 'eq'): return all(look(lab[r]) == r for r in f[1:])
    raise ValueError(f)

def conflicts(f):
    """pairs (r, s): s is bound inside the scope of r while r is still referenced inside s's scope
    -> r and s need different labels.  Also two roles occurring in one atom."""
    out = set()
    def refs(g):
        if isinstance(g, str): return set()
        h = g[0]
        if h in ('el', 'eq'): return set(g[1:])
        if h in ('all', 'ex'): return refs(g[2])          # g[1] bound here (may be referenced)
        if h == 'not': return refs(g[1])
        return refs(g[1]) | refs(g[2])
    def walk(g, env):
        if isinstance(g, str): return
        h = g[0]
        if h in ('all', 'ex'):
            inner = refs(g[2])
            for r in env:
                if r in inner and r != g[1]: out.add(frozenset((r, g[1])))
            walk(g[2], env + [g[1]])
        elif h == 'not': walk(g[1], env)
        elif h in ('im', 'and', 'or'): walk(g[1], env); walk(g[2], env)
    walk(f, [])
    return out

def greedy_labels(f, order=None, labels=range(1, 12), rng=None):
    rs = roles(f)
    cf = conflicts(f)
    if order is None: order = rs
    lab = {}
    for r in order:
        used = {lab[s] for s in lab if frozenset((r, s)) in cf}
        cands = [l for l in labels if l not in used]
        lab[r] = cands[0] if rng is None else (cands[0] if rng.random() < 0.7 else rng.choice(cands[:3]))
    assert check(f, lab), 'labeling captured a variable'
    return lab

# ---- bundle assembly and compilation
def orig_tokens():
    return gen.rpn(gen.orig())

def bundle_tokens(ng_toks, place='after'):
    o = orig_tokens()
    if place == 'after': return o + ng_toks + ['wa']
    if place == 'before': return ng_toks + o + ['wa']
    # inside: (C∧G') ∧ ((V∈∧V=) ∧ NG)   /  ((C∧G') ∧ NG) ∧ V
    of = gen.orig()
    CG, V = of[1], of[2]
    if place == 'inV': return gen.rpn(CG) + gen.rpn(V) + ng_toks + ['wa', 'wa']
    if place == 'inV2': return gen.rpn(CG) + ng_toks + gen.rpn(V) + ['wa', 'wa']
    if place == 'inCG': return gen.rpn(CG) + ng_toks + ['wa'] + gen.rpn(V) + ['wa']
    raise ValueError(place)

def compile_tokens(btoks, name='ngtmp', save=None):
    src, j, k, items = gen.load_axioms_items()
    new = items[:gen.BUNDLE_START] + btoks + items[gen.GATE_START:]
    out = src[:j + 8] + ', '.join(new) + src[k - 1:]
    path = os.path.join(HERE, f'source_{name}.py')
    open(path, 'w', encoding='utf-8').write(out)
    import importlib
    mod = importlib.import_module(f'source_{name}')
    importlib.reload(mod)
    z = mod.ZF2(); z.debug = False
    z.build_machine()
    if save:
        z.tm.save(os.path.join(HERE, save))
    return len(set(s[0] for s in z.tm.states))

def measure(f, lab=None, place='after', name='ngtmp'):
    if lab is None: lab = greedy_labels(f)
    assert check(f, lab)
    t = rpn(f, lab)
    return compile_tokens(bundle_tokens(t, place), name), len(t), lab

# ---- pretty printing
def show(f, lab=None):
    n = (lambda r: f'v{lab[r]}') if lab else (lambda r: r)
    if isinstance(f, str): return '⊥' if f == FALSUM else n(f)
    h = f[0]
    if h == 'el': return f'{n(f[1])}∈{n(f[2])}'
    if h == 'eq': return f'{n(f[1])}={n(f[2])}'
    if h == 'im': return f'({show(f[1], lab)} → {show(f[2], lab)})'
    if h == 'and': return f'({show(f[1], lab)} ∧ {show(f[2], lab)})'
    if h == 'or': return f'({show(f[1], lab)} ∨ {show(f[2], lab)})'
    if h == 'not': return f'¬{show(f[1], lab)}'
    if h == 'all': return f'∀{n(f[1])} {show(f[2], lab)}'
    if h == 'ex': return f'∃{n(f[1])} {show(f[2], lab)}'

def debruijn(f, lab, env=()):
    """de Bruijn reading (library order: $0 = innermost binder).  Falsity is shown as ⊥ (the code-1
    literal v0∈v0 is read as ⊥ after IR normalisation)."""
    if isinstance(f, str): return '⊥'
    h = f[0]
    def ix(r):
        l = lab[r]
        for i, k in enumerate(reversed(env)):
            if k == l: return f'${i}'
        raise ValueError('free ' + r)
    if h == 'el': return f'{ix(f[1])}∈{ix(f[2])}'
    if h == 'eq': return f'{ix(f[1])}={ix(f[2])}'
    if h == 'not': return f'¬{debruijn(f[1], lab, env)}'
    if h in ('im', 'and', 'or'):
        op = {'im': '→', 'and': '∧', 'or': '∨'}[h]
        return f'({debruijn(f[1], lab, env)} {op} {debruijn(f[2], lab, env)})'
    q = '∀' if h == 'all' else '∃'
    return f'{q}[{debruijn(f[2], lab, env + (lab[f[1]],))}]'
