"""PA machine variants (formula ASTs for pagen).  python pavars.py [name ...]"""
import sys
from pagen import *

# ---------------------------------------------------------------- m254 rows (logic core)
GEN = al('a', 'h')
L = im(im(im('c', 'u'), 'a'), im(im('a', 'c'), im('b', 'c')))         # Łukasiewicz
EUC = im(eq('c', 'a'), eq('c', 'b'), eq('a', 'b'))
B6C = im(ex('a', al('a', 'b')), 'b')
COMM = im(al('a', al('b', 'c')), al('b', al('a', 'c')))
QI = im(al('a', im('b', 'c')), im(al('a', 'b'), al('a', 'c')))
R1 = ex('a', eq('a', 'b'))
LC = im(eq('c', 'a'), rel('c', 'b'), rel('a', 'b'))                   # left congruence (old rho5)
# m254 rho3 (a=b -> (c e a -> c e b)) is NOT valid here (a, b are term codes on the right)

# ---------------------------------------------------------------- PA logic rows
FUN = im(rel('a', 'b'), rel('c', 'b'), eq('a', 'c'))                  # functionality, any term code b
EXd = ex('d', rel('d', 'c'))                                          # ∃x x==T(c), x = c+1 fresh
CS = im(eq('a', 'b'), rel('c', S('a')), rel('c', S('b')))
CA1 = im(eq('a', 'b'), rel('c', add('a', 'd')), rel('c', add('b', 'd')))
CA2 = im(eq('a', 'b'), rel('c', add('d', 'a')), rel('c', add('d', 'b')))
CM1 = im(eq('a', 'b'), rel('c', mul('a', 'd')), rel('c', mul('b', 'd')))
CM2 = im(eq('a', 'b'), rel('c', mul('d', 'a')), rel('c', mul('d', 'b')))
CONG = [CS, CA1, CA2, CM1, CM2]

# ---------------------------------------------------------------- Q / FA (library orientation), open
# x=a y=b u=c w=d v=0
QZS = im(rel('a', Z), no(rel('a', S('b'))))                           # ¬ 0 == σx
QINJ = im(rel('c', S('a')), rel('c', S('b')), eq('a', 'b'))           # σx==σy → x==y
QAZ = im(rel('a', Z), rel('b', add('a', 'b')))                        # 0 ⊕ x == x
QAR = im(rel('c', S('a')), rel('d', add('a', 'b')), rel('0', S('d')), rel('0', add('c', 'b')))  # σx⊕y == σ(x⊕y)
QMZ = im(rel('a', Z), rel('a', mul('a', 'b')))                        # 0 ⊗ x == 0
QMR = im(rel('c', S('a')), rel('d', mul('a', 'b')), rel('0', add('b', 'd')), rel('0', mul('c', 'b')))  # σx⊗y == y⊕x⊗y
QAX = [QZS, QINJ, QAZ, QAR, QMZ, QMR]

# ---------------------------------------------------------------- NG (closed; numeric labels)
def ng(z='0', o='1', m='2', n='3', q='4'):
    big = lambda x: an(no(eq(x, z)), no(eq(x, o)))
    pr = lambda x: an(big(x), al(z, al(m, im(rel(x, mul(z, m)), orr(eq(z, o), eq(m, o))))))
    return ex(z, ex(o, ex(m, ands(rel(z, Z), rel(o, S(z)),
                                   ex(n, an(rel(m, add(n, n)), big(n))),
                                   al(n, al(q, im(rel(m, add(n, q)), no(an(pr(n), pr(q))))))))))
NG = ng()

# ---------------------------------------------------------------- gated bundle
IND = im(al('a', im(rel('a', Z), PHI)),
         al('a', im(PHI, al('c', im(rel('c', S('a')), al('a', im(eq('a', 'c'), PHI)))))),
         al('a', PHI))
VEQ = im(eq('a', 'b'), al('c', eq('a', 'b')))
VS = im(rel('a', S('b')), al('c', rel('a', S('b'))))
VZ = im(rel('a', Z), al('c', rel('a', Z)))
VA = im(rel('a', add('b', 'd')), al('c', rel('a', add('b', 'd'))))
VM = im(rel('a', mul('b', 'd')), al('c', rel('a', mul('b', 'd'))))
LZ = im(eq('a', 'c'), PHI, al('a', im(eq('a', 'c'), PHI)))             # Leibniz schema

def flat1():
    rows = [L, EUC, B6C, LC, COMM, QI, R1, FUN, EXd] + CONG + QAX + [NG]
    bundle = ands(IND, VEQ, VS, VZ, VA, VM)
    return [GEN], rows, bundle

def flat1_lz():          # Leibniz schema replaces LC and the five term congruences
    rows = [L, EUC, B6C, COMM, QI, R1, FUN, EXd] + QAX + [NG]
    bundle = ands(IND, LZ, VEQ, VS, VZ, VA, VM)
    return [GEN], rows, bundle

def core_only():         # m254 logic rows only + IND (cost reference)
    rows = [L, EUC, B6C, LC, COMM, QI, R1]
    return [GEN], rows, ands(IND, VEQ)

VARIANTS = {k: v for k, v in dict(globals()).items() if callable(v) and k in
            ('flat1', 'flat1_lz', 'core_only')}

# ---- cheap NG (ng2): Big(y) := ¬ y==y⊗y ; Pr(y) := Big(y) ∧ ∀m∀n(y==m⊗n → m==y ∨ n==y); one Pr occurrence
def ng2(m='1', n='0', q='3', x='2'):
    big = lambda y: no(rel(y, mul(y, y)))
    pr = lambda y: an(big(y), al(m, al(n, im(rel(y, mul(m, n)), orr(eq(m, y), eq(n, y))))))
    bad = no(al(x, im(orr(eq(x, n), eq(x, q)), pr(x))))
    body = al(n, al(q, im(rel(m, add(n, q)), bad)))
    return ex(m, ex(n, ands(rel(m, add(n, n)), big(n), body)))
LOGIC = [L, EUC, B6C, COMM, QI, R1, FUN, EXd]
def mk(ngf, lz=True, extra_b=(), drop_b=()):
    rows = LOGIC + ([] if lz else [LC] + CONG) + QAX + [ngf]
    b = [IND] + ([LZ] if lz else []) + [VEQ, VS, VZ, VA, VM]
    b = [x for x in b if all(x is not y for y in drop_b)] + list(extra_b)
    return [GEN], rows, ands(*b)
VARIANTS.update({
    'lz_ng2': lambda: mk(ng2()),
    'cong_ng2': lambda: mk(ng2(), lz=False),
    'lz_ngstd': lambda: mk(NG),
    'lz_ng2_noVZ': lambda: mk(ng2(), drop_b=[VZ]),
    'lz_noNG': lambda: (lambda p: (p[0], p[1][:-1], p[2]))(mk(ng2())),
})

if __name__ == '__main__':
    names = sys.argv[1:] or list(VARIANTS)
    for n in names:
        pre, post, b = VARIANTS[n]()
        ns, nt = build('v_' + n, pre, post, b)
        print(f'{n:12s} tokens {nt:4d} states {ns}', flush=True)
