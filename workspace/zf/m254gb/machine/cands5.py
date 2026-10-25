"""NG' family E: one 'partition' block reused for the Goldbach split, the grid rows and the grid
columns.  Role names are reused on purpose (rebinding), so that equal sub-formulas get equal text.

NG_E = ∃n [ Ev ∧ GF ]
  Part(n,R) = ∀x∈n ∃!r∈R x∈r  ∧  ∀r∈R ∀u∈r u∈n             (R partitions n; empty blocks allowed)
  Two(R)    = ∃c∈R ∃d∈R ∀e∈R (e=c ∨ e=d)                     (1 ≤ |R| ≤ 2)
  NT(n,R)   = ∀r∈R ∃x∈n ¬x∈r                                 (|R| ≥ 2 when n ≠ ∅)
  Half(R,C) = Part(n,R) ∧ NT(n,R)
  G(R,C)    = ∀r∈R ∀c∈C ∃!x∈r x∈c
  Grid      = Half(R,C) ∧ Half(C,R) ∧ G(R,C)                 (Half(C,R) through a swap)
  Comp(n)   = ∃R ∃C Grid                                     (|n| = |R|·|C|, both ≥ 2)
  Ev        = ∃R ∃C (Grid ∧ Two(R))                          (n even, n ≥ 4)
  GF        = ∀R ( Part(n,R) ∧ Two(R) → ( ∀Y∈R LM(Y) ∧ ∃n∈R (Small(n) ∨ Comp(n)) ) )
  LM(Y)     = ∀z∈Y ( ∃m∈Y ∃M∈Y ∀k∈Y ((m∈k ∨ m=k) ∧ ¬M∈k)  ∧  ∀w∈z w∈n )
  Small(n)  = ∃y ∀x∈n x=y
Inside GF, ∃n∈R rebinds n to a block (the outer n is no longer used there).
"""
import itertools
from ngdsl import *

def A2(p, q, flip): return an(q, p) if flip else an(p, q)

def perm_and(ps, k, left=0):
    ps = [ps[i] for i in list(itertools.permutations(range(len(ps))))[k % len(list(itertools.permutations(range(len(ps)))))]]
    if len(ps) == 1: return ps[0]
    if left:
        acc = ps[0]
        for p in ps[1:]: acc = an(acc, p)
        return acc
    return ands(*ps)

def exone(v, S, P, Pw, w, f=0, form=0):
    if form == 0:
        return ex(v, an(el(v, S), A2(P, al(w, im(el(w, S), im(Pw, eq(w, v)))), f)))
    return ex(v, an(el(v, S), A2(P, al(w, im(an(el(w, S), Pw), eq(w, v))), f)))

def part(o):
    rowu = ball('px', 'n', exone('pr', 'R', el('px', 'pr'), el('px', 'ps'), 'ps', o['e1f'], o['exf']))
    rs = ball('qr', 'R', ball('qx', 'qr', el('qx', 'n')))
    return A2(rowu, rs, o['ptf'])

def two(o):
    # R = {c, d} with c, d ∈ R (so R ≠ ∅; this excludes n = 0 in Ev, where the 0×0 grid exists)
    return bex('tc', 'R', bex('td', 'R', ball('te', 'R', orr(eq('te', 'tc'), eq('te', 'td')))))

def nt(o):
    return ball('nr', 'R', bex('nx', 'n', no(el('nx', 'nr'))))

def half(o):
    return A2(part(o), nt(o), o['hf'])

def G(o):
    return ball('gr', 'R', ball('gc', 'C', exone('gx', 'gr', el('gx', 'gc'), el('gy', 'gc'), 'gy', o['e2f'], o['exf'])))

def grid(o):
    h = half(o)
    sw = ex('T', an(eq('T', 'R'), ex('R', an(eq('R', 'C'), ex('C', an(eq('C', 'T'), h))))))
    if o['swapform'] == 1:     # swap through C first
        sw = ex('T', an(eq('T', 'C'), ex('C', an(eq('C', 'R'), ex('R', an(eq('R', 'T'), h))))))
    return perm_and([h, sw, G(o)], o['gp'], o['gl'])

def comp(o):
    return ex('R', ex('C', grid(o)))

def ev(o):
    return ex('R', ex('C', A2(grid(o), two(o), o['evf'])))

def small(o):
    return ex('ky', ball('kx', 'n', eq('kx', 'ky')))

def lm(o):
    Y = 'Y'
    body = bex('lm', Y, bex('lM', Y, ball('lk', Y, A2(orr(el('lm', 'lk'), eq('lm', 'lk')), no(el('lM', 'lk')), o['lmf']))))
    body = A2(body, ball('lw', 'lz', el('lw', 'n')), o['trf'])
    return ball('lz', Y, body)

def gf(o):
    hyp = A2(part(o), two(o), o['gh'])
    np_ = orr(small(o), comp(o)) if not o['npf'] else orr(comp(o), small(o))
    concl = A2(ball('Y', 'R', lm(o)), bex('n', 'R', np_), o['gcf'])
    return al('R', im(hyp, concl))

def ngE(o):
    return ex('n', A2(ev(o), gf(o), o['topf']))

OPTS = {'e1f': 2, 'e2f': 2, 'exf': 2, 'ptf': 2, 'hf': 2, 'swapform': 2, 'gp': 6, 'gl': 2, 'evf': 2,
        'lmf': 2, 'trf': 2, 'gh': 2, 'npf': 2, 'gcf': 2, 'topf': 2}
DEFAULT = {k: 0 for k in OPTS}

if __name__ == '__main__':
    import sys
    o = dict(DEFAULT)
    for kv in sys.argv[1:]:
        k, v = kv.split('='); o[k] = int(v)
    f = ngE(o)
    lab = greedy_labels(f)
    print(show(f))
    print(len(roles(f)), 'roles; labels', lab)
    st, nt_, _ = measure(f, lab)
    print('tokens', nt_, 'states', st)
