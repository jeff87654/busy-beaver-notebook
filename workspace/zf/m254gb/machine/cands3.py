"""NG' family C (refinement of cands2): all role names fixed so that labels can be searched.

NG_C = ∃n [ Ev(n) ∧ GF(n) ]          (Tr(n) folded into LM, see below)
  GF(n)    = ∀A ∀B ( Split(A,B) → ( LM(A) ∧ ∃X ((X=A ∨ X=B) ∧ (Small(X) ∨ Comp(X))) ) )
  Split    = ∀x ( (x∈n → x∈A ∨ x∈B) ∧ ((x∈A ∨ x∈B → x∈n) ∧ (x∈A → ¬x∈B)) )
  LM(A)    = ∀z∈A ( Least ∧ Max [∧ ∀w∈z w∈n] )       (A ranges over all subsets of n; A = n gives Tr(n))
  Small(X) = ∃y ∀x∈X x=y
  Comp(X)  = ∃R ∃C ( Grid(R,C) ∧ (X=n → Two(C)) )
  Grid     = Half(R,C) ∧ Half(C,R) [∧ G(R,C)]     with  Half = RowU ∧ NT [∧ G]
  RowU     = ∀x∈X ∃!r∈R x∈r       NT = ∀r∈R ∃x∈X ¬x∈r      G = ∀r∈R ∀c∈C ∃!x∈X (x∈r ∧ x∈c)
  Two(C)   = ∃c ∃d ∀e∈C (e=c ∨ e=d)
  Ev(n)    = ∃X (X=n ∧ Comp(X))
Options (o): see OPTS.
"""
import itertools
from ngdsl import *

def A2(p, q, flip): return an(q, p) if flip else an(p, q)

def tri(ps, perm, left):
    ps = [ps[i] for i in list(itertools.permutations(range(len(ps))))[perm]]
    if len(ps) == 2: return an(ps[0], ps[1])
    return an(an(ps[0], ps[1]), ps[2]) if left else an(ps[0], an(ps[1], ps[2]))

def exone(v, S, P, Pw, w, f=0, form=0):
    if form == 0:   # ∃v (v∈S ∧ (P(v) ∧ ∀w (w∈S → (P(w) → w=v))))
        return ex(v, an(el(v, S), A2(P, al(w, im(el(w, S), im(Pw, eq(w, v)))), f)))
    # form 1: ∃v (v∈S ∧ (P(v) ∧ ∀w ((w∈S ∧ P(w)) → w=v)))
    return ex(v, an(el(v, S), A2(P, al(w, im(an(el(w, S), Pw), eq(w, v))), f)))

def G(X, R, C, o):
    P = A2(el('gx', 'gr'), el('gx', 'gc'), o['pf']); Pw = A2(el('gy', 'gr'), el('gy', 'gc'), o['pf'])
    return ball('gr', R, ball('gc', C, exone('gx', X, P, Pw, 'gy', o['e2f'], o['exf'])))

def half(X, R, C, o):
    rowu = ball('hx', X, exone('hr', R, el('hx', 'hr'), el('hx', 'hs'), 'hs', o['e1f'], o['exf']))
    nt = ball('nr', R, bex('nx', X, no(el('nx', 'nr'))))
    if o['gsep']:
        return A2(rowu, nt, o['hp'] % 2)
    return tri([rowu, nt, G(X, R, C, o)], o['hp'], o['hl'])

def two(C):
    return ex('tc', ex('td', ball('te', C, orr(eq('te', 'tc'), eq('te', 'td')))))

def comp(X, n, o):
    h = half(X, 'R', 'C', o)
    if o['swapform'] == 0:
        sw = ex('T', an(eq('T', 'R'), ex('R', an(eq('R', 'C'), ex('C', an(eq('C', 'T'), h))))))
        core = A2(h, sw, o['swf'])
    else:   # ∀P∀Q (((P=R ∧ Q=C) ∨ (P=C ∧ Q=R)) → Half(P,Q))   with P,Q labelled like R,C... (roles P,Q)
        hpq = half(X, 'P', 'Q', o)
        core = al('P', al('Q', im(orr(an(eq('P', 'R'), eq('Q', 'C')), an(eq('P', 'C'), eq('Q', 'R'))), hpq)))
    if o['gsep']:
        core = A2(core, G(X, 'R', 'C', o), o['gsf'])
    guard = im(eq(X, n), two('C'))
    return ex('R', ex('C', A2(core, guard, o['gf'])))

def small(X):
    return ex('ky', ball('kx', X, eq('kx', 'ky')))

def split(n, A, B, o):
    OR = orr(el('px', A), el('px', B))
    return al('px', A2(im(el('px', n), OR), A2(im(OR, el('px', n)), im(el('px', A), no(el('px', B))), o['spf2']), o['spf']))

def lm(A, n, o):
    if o['lmm']:      # merged: ∃m∈A ∃M∈A ∀k∈A ((m∈k ∨ m=k) ∧ ¬M∈k)
        body = bex('lm', A, bex('lM', A, ball('lk', A, A2(orr(el('lm', 'lk'), eq('lm', 'lk')), no(el('lM', 'lk')), o['lmf']))))
    else:
        least = bex('lm', A, ball('lk', A, orr(el('lm', 'lk'), eq('lm', 'lk'))))
        mx = bex('lM', A, ball('lk2', A, no(el('lM', 'lk2'))))
        body = A2(least, mx, o['lmf'])
    if o['trin']:
        body = A2(body, ball('lw', 'lz', el('lw', n)), o['trf'])
    return ball('lz', A, body)

def tr(n):
    return ball('ty', n, ball('tz', 'ty', el('tz', n)))

def ngC(o):
    n, A, B, X = 'n', 'A', 'B', 'X'
    cp = comp(X, n, o)
    ch = orr(eq(X, A), eq(X, B))
    np_ = orr(small(X), cp) if not o['npf'] else orr(cp, small(X))
    gfb = A2(lm(A, n, o), ex(X, A2(ch, np_, o['chf'])), o['lmpos'])
    gf = al(A, al(B, im(split(n, A, B, o), gfb)))
    ev = ex(X, A2(eq(X, n), cp, o['evf']))
    if o['trin']:
        body = A2(ev, gf, o['topp'] % 2)
    else:
        body = tri([tr(n), ev, gf], o['topp'], o['topl'])
    return ex(n, body)

OPTS = {'e1f': 2, 'e2f': 2, 'exf': 2, 'pf': 2, 'hp': 6, 'hl': 2, 'gsep': 2, 'gsf': 2, 'swapform': 2,
        'swf': 2, 'gf': 2, 'spf': 2, 'spf2': 2, 'lmm': 2, 'lmf': 2, 'trin': 2, 'trf': 2, 'npf': 2,
        'chf': 2, 'lmpos': 2, 'evf': 2, 'topp': 6, 'topl': 2}
DEFAULT = {k: 0 for k in OPTS}
DEFAULT.update({'trin': 1, 'lmm': 1})

if __name__ == '__main__':
    import sys
    o = dict(DEFAULT)
    for kv in sys.argv[1:]:
        k, v = kv.split('='); o[k] = int(v)
    f = ngC(o)
    lab = greedy_labels(f)
    print(show(f))
    print(len(roles(f)), 'roles; labels', lab)
    st, nt, _ = measure(f, lab)
    print('tokens', nt, 'states', st)
