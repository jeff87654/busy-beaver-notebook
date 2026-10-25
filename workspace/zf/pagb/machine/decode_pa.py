"""Decoded reading of the PA machine.

1. `python decode_pa.py` : symbolically runs the compiled source's axioms() (extract_rpn, no hand
   transcription) and prints every AX root in PA notation, reading the second argument of Rel as a
   term code:  T(4P(j,k)+0) = σ v_j (canonical k = j),  +1 = v_j ⊕ v_k,  +2 = v_j ⊗ v_k,  +3 = 0.
   Labels: a = param1, h = cache (GEN only), b = param2 after its read, c = selector-3, c+1, c+2,
   u = literal, numerals = fixed labels.
2. `D(n)` / `Tm(n)` : the numeric decoder (formula / term codes -> strings), used by tests.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bignum import unP

# ---------------------------------------------------------------- numeric decoder
def Tm(n):
    q, t = divmod(n, 4); j, k = unP(q)
    if t == 0: return f'σv{j}' if k == j else f'σv{j}[junk {k}]'
    if t == 1: return f'(v{j} ⊕ v{k})'
    if t == 2: return f'(v{j} ⊗ v{k})'
    return '0'

def D(n):
    if n == 0: return '⊤'
    if n == 1: return 'F'
    q, t = divmod(n, 4); x, y = unP(q)
    if t == 0:
        return f'¬{D(x)}' if y == 1 else f'({D(x)} → {D(y)})'
    if t == 1: return f'v{x} = {Tm(y)}'
    if t == 2: return f'∀v{x} {D(y)}'
    return f'v{x} = v{y}'

# ---------------------------------------------------------------- symbolic (from the compiled source)
def lab(x):
    if isinstance(x, int): return f'v{x}'
    if isinstance(x, tuple) and x[0] == 'Succ':
        k = 1; y = x[1]
        while isinstance(y, tuple) and y[0] == 'Succ': k += 1; y = y[1]
        return f'{lab(y)}+{k}'
    return {'B': 'b', 'b': 'h', 'q': 'u'}.get(x, x)

A_MODE = os.environ.get('PA_DESIGN', 'A') == 'A'

def termA(t):
    """design A: 0 = zero, Imp(t,·) = σt, Rel = ⊕, All = ⊗, Eq(i,·) = v_i; a raw parameter = T(param)."""
    if t == 0: return '0'
    if isinstance(t, tuple) and t[0] == 'Eq': return 'v' + lab(t[1]) if not isinstance(t[1], int) else f'v{t[1]}'
    if isinstance(t, tuple) and t[0] == 'Imp': return f'σ{termA(t[1])}'
    if isinstance(t, tuple) and t[0] in ('Rel', 'All'):
        return f'({termA(t[1])} {"⊕" if t[0] == "Rel" else "⊗"} {termA(t[2])})'
    if isinstance(t, tuple) and t[0] == 'Succ': return f'T({lab(t)})'
    return f'T({lab(t)})'

def term(t):
    """decode a term code (possibly nested): Imp tag = σ, Rel = ⊕, All = ⊗, Eq(0,0)/3 = 0."""
    if A_MODE: return termA(t)
    if t == 3: return '0'
    if isinstance(t, tuple) and t[0] == 'Eq' and t[1] == 0 and t[2] == 0: return '0'
    if isinstance(t, tuple) and t[0] in ('Imp', 'Rel', 'All'):
        j, k = term(t[1]), term(t[2])
        if t[0] == 'Imp': return f'σ{j}' if k == j else f'σ({j})[{k}]'
        return f'({j} {"⊕" if t[0] == "Rel" else "⊗"} {k})'
    return lab(t)                  # a variable term (label or small index)

def show(f):
    if isinstance(f, int):
        return {0: '⊤', 1: 'F'}.get(f, f'#{f}')
    if isinstance(f, str):
        return {'a': 'A', 'c': 'Φ', 'B': 'B', 'b': 'H', 'q': 'U', 'T': 't'}.get(f, f)   # formula positions
    h = f[0]
    if h == 'Succ':
        return lab(f)
    if h == 'Imp' and f[2] == 1:
        a = f[1]
        if isinstance(a, tuple) and a[0] == 'Imp' and isinstance(a[2], tuple) and a[2][0] == 'Imp' and a[2][2] == 1:
            return f'({show(a[1])} ∧ {show(a[2][1])})'
        if isinstance(a, tuple) and a[0] == 'All' and isinstance(a[2], tuple) and a[2][0] == 'Imp' and a[2][2] == 1:
            return f'∃{lab(a[1])} {show(a[2][1])}'
        if isinstance(a, tuple) and a[0] == 'Imp' and isinstance(a[1], tuple) and a[1][0] == 'Imp' and a[1][2] == 1:
            pass
        return f'¬{show(a)}'
    if h == 'Imp':
        a = f[1]
        isex = (isinstance(a, tuple) and a[0] == 'Imp' and a[2] == 1 and isinstance(a[1], tuple)
                and a[1][0] == 'All' and isinstance(a[1][2], tuple) and a[1][2][0] == 'Imp' and a[1][2][2] == 1)
        if isinstance(a, tuple) and a[0] == 'Imp' and a[2] == 1 and not isex:     # ¬A → B  =  A ∨ B
            return f'({show(a[1])} ∨ {show(f[2])})'
        return f'({show(f[1])} → {show(f[2])})'
    if h == 'All':
        return f'∀{lab(f[1])} {show(f[2])}'
    if h == 'Eq':
        return f'{term(f[1])} = {term(f[2])}'
    if h == 'Rel' and A_MODE:
        return f'σ{term(f[1])} = {term(f[2])}'
    if h == 'Rel':
        return f'{lab(f[1])} = {term(f[2])}'
    raise ValueError(f)

def conj(f):
    if isinstance(f, tuple) and f[0] == 'Imp' and f[2] == 1:
        a = f[1]
        if isinstance(a, tuple) and a[0] == 'Imp' and isinstance(a[2], tuple) and a[2][0] == 'Imp' and a[2][2] == 1:
            return conj(a[1]) + conj(a[2][1])
    return [f]

if __name__ == '__main__':
    import design
    os.environ['M254TG_SRC'] = 'source_pa' + design.SUFFIX
    if not os.path.exists(os.path.join(HERE, f'source_pa{design.SUFFIX}.py')):
        design.build_files()
    import extract_rpn as E
    tw, ws, gates = E.axioms_symbolic(ninit=0)
    print('AX roots, bottom of stack to top (t = old current formula):')
    for i, f in enumerate(ws):
        print(f'  slot {i:2d}: {show(f)}')
    print('Upper case = formula positions (Φ = decode(c)); lower case = variable labels.')
    g = getattr(design, 'GATE', 'ab')
    cond = {'ab': 'c ∉ {a, b}', 'abu': 'c ∉ {a, b, u}', 'occ': 'c ∉ vars T(a) ∪ vars T(b)'}[g]
    print(f'current (gated: {cond}, else ⊤), conjuncts:')
    for i, f in enumerate(conj(tw)):
        print(f'  B{i}: {show(f)}')
    print('gate ops:', len(gates))
