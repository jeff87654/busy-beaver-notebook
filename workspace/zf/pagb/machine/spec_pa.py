"""Abstract specification of one run of main() of the PA source (source_pa.py).

Identical to the zfc_254 spec (m254/logic/spec.py) except for the AX roots: AX pushes the old current
formula, GEN of the cache, the rows of design.ROWS (in order), and leaves the gated bundle current.

The codes of the roots are computed here DIRECTLY from the formula ASTs of design.py (by evaluating
the AST with the code functions below).  The machine computes them by running RPN token lists through
the stack constructors; validate_pa.py checks the two agree.

State (pl, np, tw, ws, d, h) = (prooflist, nextproof, topwff, wffstack, param1, param2).
Coding: dual Cantor P(a,b) = tri(a+b)+b.  Imp = 4P+0, Rel = 4P+1, All = 4P+2, Eq = 4P+3.
Term codes: σx = 4P(x,x)+0, x⊕y = 4P(x,y)+1, x⊗y = 4P(x,y)+2, zero = 3.
"""
from bignum import P, unP, add, norm

def _code(tag, a, b): return add(norm(4 * P(a, b)), tag)
def wim(a, b): return _code(0, a, b)
def wel(i, j): return _code(1, i, j)
def wal(i, a): return _code(2, i, a)
def weq(i, j): return _code(3, i, j)
F = 1
def wn(a): return wim(a, F)
def wa(a, b): return wn(wim(a, wn(b)))
def wex(x, a): return wn(wal(x, wn(a)))
def tS(x): return _code(0, x, x)
def tadd(x, y): return _code(1, x, y)
def tmul(x, y): return _code(2, x, y)
ZERO = 3

def ev(f, env):
    """evaluate a design AST to its code; env maps 'a','b','c','u','h' (and derived 'd','e')."""
    if isinstance(f, str):
        if f in env: return env[f]
        if f == 'd': return add(env['c'], 1)
        if f == 'e': return add(env['c'], 2)
        if f == 'phi': return env['c']
        if f == 'Z': return ZERO
        if f == 'Z0': return 0
        if f == 'F': return F
        if f.isdigit(): return int(f)
        raise KeyError(f)
    h = f[0]
    if h == 'not': return wn(ev(f[1], env))
    if h == 'S': return tS(ev(f[1], env))
    if h == 'V': return weq(ev(f[1], env), 0)
    if h == 'S1': return wim(ev(f[1], env), 1)
    if h == 'teq': return weq(ev(f[1], env), ev(f[2], env))
    if h == 'srel': return wel(ev(f[1], env), ev(f[2], env))
    x, y = ev(f[1], env), ev(f[2], env)
    if h == 'or': return wim(wn(x), y)
    return {'rel': wel, 'eq': weq, 'im': wim, 'all': wal, 'ex': wex, 'and': wa,
            'add': tadd, 'mul': tmul}[h](x, y)

import design

def ax_rows(a, h, b, c, u):
    """slots pushed by AX above the old current formula, bottom to top (GEN first)."""
    env0 = {'a': a, 'h': h, 'c': c}
    out = [ev(r, env0) for r in design.PRE]
    env = {'a': a, 'b': b, 'c': c, 'u': u}
    out += [ev(r, env) for r in design.ROWS]
    return out

def bundle(a, b, c, u=0):
    return ev(design.BUNDLE, {'a': a, 'b': b, 'c': c, 'u': u})

def tvars(n):
    """variable indices of the design-A term T(n) (exact ints only)."""
    out = set(); todo = [n]
    while todo:
        x = todo.pop()
        if x == 0: continue
        q, t = divmod(x, 4); j, k = unP(q)
        if t == 3: out.add(j)
        elif t == 0: todo.append(j)
        else: todo += [j, k]
    return out

def gate_open(a, b, c, u=0):
    g = getattr(design, 'GATE', 'ab')
    if g == 'ab': return c != a and c != b
    if g == 'abu': return c != a and c != b and c != u
    return c not in tvars(a) and c not in tvars(b)          # 'occ'

def gated_bundle(a, b, c, u=0):
    return bundle(a, b, c, u) if gate_open(a, b, c, u) else 0

def enum_step(s):
    pl, np, tw, ws, d, h = s
    if pl == 0:
        pl, np = np, np + 1
    else:
        pl -= 1
    ac, pl = unP(pl)
    x, pl = unP(pl)
    d += x
    if ac == 0:                                   # MP
        if wim(tw, d) == h:
            tw, ws = d, P(0, ws)
        else:
            tw = 0
        h = 0
    elif ac == 1:                                 # DROP: push current, current := cache
        tw, ws = h, P(tw, ws)
    elif ac == 2:                                 # NIP: halt on cache F, else cache := pop
        if h == 1:
            return None
        h, ws = unP(ws)
    else:                                         # AX
        c = ac - 3; a = d
        y, pl = unP(pl); b = add(h, y)
        u, pl = unP(pl)
        for r in [tw] + ax_rows(a, h, b, c, u):
            ws = P(r, ws)
        tw = gated_bundle(a, b, c, u)
        d = 0; h = 0
    return (pl, np, tw, ws, d, h)

NSLOTS = 1 + len(design.PRE) + len(design.ROWS)    # pushed by AX (old current included)
