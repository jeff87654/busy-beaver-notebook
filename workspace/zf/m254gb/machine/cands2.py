"""Compact NG' candidates (family B).

NG_B = ∃n [ Tr(n) ∧ ( Ev(n) ∧ GF(n) ) ]
  Tr(n)    = ∀y∈n ∀z∈y z∈n
  GF(n)    = ∀A ∀B ( Split(A,B) → ( LM(A) ∧ ∃X ((X=A ∨ X=B) ∧ (Small(X) ∨ Comp(X))) ) )
  Split    = ∀x ( (x∈n → x∈A ∨ x∈B) ∧ ((x∈A ∨ x∈B → x∈n) ∧ (x∈A → ¬x∈B)) )
  LM(A)    = ∀z∈A ( ∃m∈A ∀k∈A (m∈k ∨ m=k)  ∧  ∃M∈A ∀k∈A ¬M∈k )   (least + strict max)
  Small(X) = ∃y ∀x∈X x=y
  Comp(X)  = ∃R ∃C ( Half(R,C) ∧ Half(C,R) ∧ (X=n → Two(C)) )        (Half(C,R) via a swap)
  Half(R,C)= ∀x∈X ∃!r∈R x∈r  ∧  ∀r∈R ∃x∈X ¬x∈r  ∧  ∀r∈R ∀c∈C ∃!x∈X (x∈r ∧ x∈c)
  Two(C)   = ∃c ∃d ∀e∈C (e=c ∨ e=d)
  Ev(n)    = ∃X (X=n ∧ Comp(X))          (the same Comp text as in GF)
"""
import itertools
from ngdsl import *
from cands import Fresh, A2

def exone(fr, v, S, P, Pw, w, f=0):
    """∃!v∈S P(v):  ∃v (v∈S ∧ (P(v) ∧ ∀w (w∈S → (P(w) → w=v))))"""
    return ex(v, an(el(v, S), A2(P, al(w, im(el(w, S), im(Pw, eq(w, v)))), f)))

def half(fr, X, R, C, o):
    x, r, s = 'hx', 'hr', 'hs'
    rowu = ball(x, X, exone(fr, r, R, el(x, r), el(x, s), s, o.get('e1f', 0)))
    r2, x2 = 'nr', 'nx'
    nt = ball(r2, R, bex(x2, X, no(el(x2, r2))))
    r3, c3, x3, y3 = 'gr', 'gc', 'gx', 'gy'
    P = A2(el(x3, r3), el(x3, c3), o.get('pf', 0)); Pw = A2(el(y3, r3), el(y3, c3), o.get('pf', 0))
    g = ball(r3, R, ball(c3, C, exone(fr, x3, X, P, Pw, y3, o.get('e2f', 0))))
    parts = [rowu, nt, g]
    perm = list(itertools.permutations(range(3)))[o.get('hp', 0)]
    ps = [parts[i] for i in perm]
    return A2(ps[0], A2(ps[1], ps[2], False), False) if not o.get('hl') else A2(A2(ps[0], ps[1], False), ps[2], False)

def two(C):
    c, d, e = 'tc', 'td', 'te'
    return ex(c, ex(d, ball(e, C, orr(eq(e, c), eq(e, d)))))

def comp(fr, X, n, o):
    R, C, T = 'R', 'C', 'T'
    h = half(fr, X, R, C, o)
    sw = ex(T, an(eq(T, R), ex(R, an(eq(R, C), ex(C, an(eq(C, T), h))))))
    core = A2(h, sw, o.get('swf', 0))
    guard = im(eq(X, n), two(C))
    return ex(R, ex(C, A2(core, guard, o.get('gf', 0))))

def small(X):
    return ex('ky', ball('kx', X, eq('kx', 'ky')))

def split(n, A, B, o):
    x = 'px'
    OR = orr(el(x, A), el(x, B))
    return al(x, A2(im(el(x, n), OR), A2(im(OR, el(x, n)), im(el(x, A), no(el(x, B))), o.get('spf2', 0)), o.get('spf', 0)))

def lm(A, o):
    z, m, k, M, k2 = 'lz', 'lm', 'lk', 'lM', 'lk2'
    least = bex(m, A, ball(k, A, orr(el(m, k), eq(m, k))))
    mx = bex(M, A, ball(k2, A, no(el(M, k2))))
    return ball(z, A, A2(least, mx, o.get('lmf', 0)))

def tr(n):
    return ball('ty', n, ball('tz', 'ty', el('tz', n)))

def ngB(o=None):
    o = o or {}
    fr = Fresh()
    n, A, B, X = 'n', 'A', 'B', 'X'
    cp = comp(fr, X, n, o)
    ch = orr(eq(X, A), eq(X, B))
    np_ = orr(small(X), cp) if not o.get('npf') else orr(cp, small(X))
    gfb = A2(lm(A, o), ex(X, A2(ch, np_, o.get('chf', 0))), o.get('lmpos', 0))
    gf = al(A, al(B, im(split(n, A, B, o), gfb)))
    ev = ex(X, A2(eq(X, n), cp, o.get('evf', 0)))
    parts = [tr(n), ev, gf]
    perm = list(itertools.permutations(range(3)))[o.get('topp', 0)]
    ps = [parts[i] for i in perm]
    body = A2(ps[0], A2(ps[1], ps[2], False), False) if not o.get('topl') else A2(A2(ps[0], ps[1], False), ps[2], False)
    return ex(n, body)

OPTS = {'e1f': 2, 'e2f': 2, 'pf': 2, 'hp': 6, 'hl': 2, 'swf': 2, 'gf': 2, 'spf': 2, 'spf2': 2,
        'lmf': 2, 'npf': 2, 'chf': 2, 'lmpos': 2, 'evf': 2, 'topp': 6, 'topl': 2}

if __name__ == '__main__':
    f = ngB()
    lab = greedy_labels(f)
    print(show(f))
    print(len(roles(f)), 'roles; labels', lab)
    st, nt, _ = measure(f, lab)
    print('tokens', nt, 'states', st)
