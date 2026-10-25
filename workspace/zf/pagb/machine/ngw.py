"""The machine's NG row as EXACTLY tau(NGw), NGw = Wn GCw from ../coq/PA_Sound.v.
GCw is not transcribed by hand: runs/GCw_coq_print.txt is coqc's `Eval vm_compute in tr (fun _ => TV 1)
GC_form` (definitions copied verbatim from PA_tr.v), parsed here.
tau: Wn a -> a -> F ;  Wal x a -> ∀v_x ;  Weq -> Eq-tag ;  TV n -> Var(n) ; TS -> σ ; TP -> ⊕ ; TM -> ⊗ ; TZ -> 0."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))

def parse_coq(path=os.path.join(HERE, 'runs', 'GCw_coq_print.txt')):
    txt = open(path, encoding='utf-8').read()
    txt = txt[txt.index('=') + 1: txt.rindex(':')]
    toks = re.findall(r'\(|\)|[A-Za-z_]+|\d+', txt)
    pos = 0
    def expr():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == '(':
            e = expr(); assert toks[pos] == ')'; pos += 1; return e
        if t.isdigit(): return int(t)
        if t == 'TZ': return ('TZ',)
        ar = {'Wal': 2, 'Wim': 2, 'Wn': 1, 'Weq': 2, 'TV': 1, 'TS': 1, 'TP': 2, 'TM': 2}[t]
        return (t,) + tuple(expr() for _ in range(ar))
    e = expr(); assert pos == len(toks)
    return e

def labels(w, acc=None):
    acc = set() if acc is None else acc
    if w[0] == 'TV': acc.add(w[1])
    elif w[0] == 'Wal': acc.add(w[1]); labels(w[2], acc)
    else:
        for x in w[1:]:
            if isinstance(x, tuple): labels(x, acc)
    return acc

def to_ast(w, ren=lambda n: n):
    h = w[0]
    L = lambda n: str(ren(n))
    if h == 'Wn': return ('not', to_ast(w[1], ren))
    if h == 'Wim': return ('im', to_ast(w[1], ren), to_ast(w[2], ren))
    if h == 'Wal': return ('all', L(w[1]), to_ast(w[2], ren))
    if h == 'Weq': return ('teq', to_ast(w[1], ren), to_ast(w[2], ren))
    if h == 'TV': return ('V', L(w[1]))
    if h == 'TS': return ('S1', to_ast(w[1], ren))
    if h == 'TP': return ('add', to_ast(w[1], ren), to_ast(w[2], ren))
    if h == 'TM': return ('mul', to_ast(w[1], ren), to_ast(w[2], ren))
    if h == 'TZ': return 'Z0'
    raise ValueError(w)

GCW = parse_coq()
NGW = ('Wn', GCW)

def ng_literal():
    return to_ast(NGW)

def ng_alpha(perm):
    """α-variant: binder names 2,4,6,8,10 -> perm[0..4] (distinct; same de Bruijn image)."""
    m = dict(zip([2, 4, 6, 8, 10], perm))
    return to_ast(NGW, lambda n: m[n])

if __name__ == '__main__':
    print('labels in GCw:', sorted(labels(GCW)))


# ---- (b) route: NG must be FLAT.  Name the numerals by a closed prefix (odd labels, unused by GCw):
#   NG_flat = ¬∀o0∀o1∀o2∀o3∀o4( o0=0 → o1=σo0 → o2=σo1 → o3=σo2 → o4=σo3 → GC'(o1,o2,o4) )
NUM_LABELS = (1, 3, 5, 7, 9)
def _num_of(t):
    k = 0
    while t[0] == 'TS': k += 1; t = t[1]
    return k if t == ('TZ',) else None
def flatten_numerals(w, o):
    """replace every closed numeral S^k 0 (k = 0..4) by the variable o[k]."""
    h = w[0]
    if h in ('TS', 'TZ'):
        k = _num_of(w)
        if k is not None: return ('TV', o[k])
        return ('TS', flatten_numerals(w[1], o))
    if h == 'TV': return w
    if h in ('TP', 'TM', 'Weq', 'Wim'): return (h, flatten_numerals(w[1], o), flatten_numerals(w[2], o))
    if h == 'Wn': return ('Wn', flatten_numerals(w[1], o))
    if h == 'Wal': return ('Wal', w[1], flatten_numerals(w[2], o))
    raise ValueError(w)
def is_flat_atom(e):
    """Weq with both sides of depth <= 1 over variables (and zero only alone)."""
    def d(t):
        if t[0] in ('TV', 'TZ'): return 0
        return 1 + max(d(x) for x in t[1:])
    def leaf_ok(t):
        return t[0] in ('TV',) or (t[0] == 'TZ')
    l, r = e[1], e[2]
    ok = lambda t: t[0] in ('TV', 'TZ') or all(x[0] == 'TV' for x in t[1:])
    return ok(l) and ok(r) and not (l[0] not in ('TV', 'TZ') and r[0] not in ('TV', 'TZ'))
def atoms(w, acc):
    if w[0] == 'Weq': acc.append(w)
    elif w[0] in ('Wim',): atoms(w[1], acc); atoms(w[2], acc)
    elif w[0] == 'Wn': atoms(w[1], acc)
    elif w[0] == 'Wal': atoms(w[2], acc)
    return acc
def ngflat_w(o=NUM_LABELS):
    gc1 = flatten_numerals(GCW, o)
    body = gc1
    defs = [('Weq', ('TV', o[0]), ('TZ',))] + [('Weq', ('TV', o[k]), ('TS', ('TV', o[k - 1]))) for k in range(1, 5)]
    for dfn in reversed(defs): body = ('Wim', dfn, body)
    for k in reversed(range(5)): body = ('Wal', o[k], body)
    return ('Wn', body)
def ng_flat(o=NUM_LABELS):
    return to_ast(ngflat_w(o))
