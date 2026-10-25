"""All machine-level pieces, as (start, target, positive) for the explorer.  Shapes (left-to-right, head last):
  N-family:  l 1 (10)^g ... groups ... (10)^B 1  G>             (B = accumulator units)
  W(j,i):    P (110)^j 1 1 (10)^(B+3) 1  E>  1 (101)^i 0^inf    (walk of the accumulator to the left)
  R(i,j):    Q (110)^i 1 1  G>  1 0 0 (101)^j 0^inf              (return after a borrow)
  Y(u,i):    0^inf (10)^u 1  E>  1 (101)^i 0^inf                 (rebuild at the left end)"""
import sys, time
from common import *
import mexp
def Wc(jvar=None, jc=0, ivar=None, ic=0, P=None):
    left = [1] + [0, 1] * 3 + [run(U, a=1), 1, 1] + [0, 1, 1] * jc + ([run((0, 1, 1), **{jvar: 1})] if jvar else []) + P
    right = [1] + [1, 0, 1] * ic + ([run((1, 0, 1), **{ivar: 1})] if ivar else []) + [BLANK]
    return ('E', left, right, '>')
def Rc(ivar=None, ic=0, jvar=None, jc=0, Q=None):
    left = [1, 1] + [0, 1, 1] * ic + ([run((0, 1, 1), **{ivar: 1})] if ivar else []) + Q
    right = [1, 0, 0] + [1, 0, 1] * jc + ([run((1, 0, 1), **{jvar: 1})] if jvar else []) + [BLANK]
    return ('G', left, right, '>')
def Yc(uvar=None, uc=0, ivar=None, ic=0, prime=False):
    left = ([1, 1] if prime else []) + [1] + [0, 1] * uc + ([run(U, **{uvar: 1})] if uvar else []) + [BLANK]
    right = [1] + [1, 0, 1] * ic + ([run((1, 0, 1), **{ivar: 1})] if ivar else []) + [BLANK]
    return ('E', left, right, '>')
Pn = [0, 1] * 3 + [run(U, n=1), 1, V('l')]          # beyond the zeros: units n+3 of a digit, then 1 l
Pz = [0, 1] * 2 + [1, BLANK]                          # the top entry with 2 units, then the leading 1
Qn = [0, 1] * 4 + [run(U, a=1), 1, 0, 1, run(U, n=1), 1, V('l')]   # B+4 digit, n+1 digit, 1 l
Qz = [0, 1] * 4 + [run(U, a=1), 1, 1, BLANK]                          # B+4 digit, top 0, leading 1
PARTS = {
  'R1':  (G(grp(0, a=1) + grp(2, n=1) + [V('l')]), G(grp(4, a=1) + grp(0, n=1) + [V('l')]), ()),
  'R2':  (G(grp(0, a=1) + list(Z) + grp(3, n=1) + [1, V('l')]), G(grp(1) + grp(4, a=1) + grp(1, n=1) + [1, V('l')]), ('a',)),
  'R2z': (G(grp(0, a=1) + list(Z) + grp(2) + [1, BLANK]), G(grp(1) + grp(4, a=1) + grp(0) + [1, BLANK]), ('a',)),
  'PRE': (G(grp(0, a=1) + [run(Z, k=1)] + list(Z) * 2 + [1, V('P')]), Wc(jvar='k', ic=1, P=[V('P')]), ('a',)),
  'WALK': (Wc(jvar='j', jc=1, ivar='i', P=[V('P')]), Wc(jvar='j', ivar='i', ic=1, P=[V('P')]), ('a',)),
  'BOR':  (Wc(ivar='k', ic=1, P=Pn), Rc(jvar='k', jc=1, Q=Qn), ('a',)),
  'BORz': (Wc(ivar='k', ic=1, P=Pz), Rc(jvar='k', jc=1, Q=Qz), ('a',)),
  'RET':  (Rc(ivar='i', jvar='j', jc=1, Q=[V('T')]), Rc(ivar='i', ic=1, jvar='j', Q=[V('T')]), ()),
  'END':  (Rc(ivar='k', ic=1, Q=[0, 1] * 4 + [run(U, a=1), 1, V('T')]),
           G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, a=1) + [1, V('T')]), ()),
  'LASTW': (Wc(ivar='i', P=[BLANK]), Yc(uvar='a', uc=3, ivar='i', ic=1), ('a',)),
  'YC':  (Yc(uvar='u', uc=1, ivar='i'), Yc(uvar='u', ivar='i', ic=2), ()),
  'YEND': (Yc(ivar='i', ic=1), G([1, 0, 1, 0, 1] + [run(Z, i=1)] + [1, 0, 1, 0, 1, BLANK]), ()),
  'BORn': (Wc(ivar='k', ic=1, P=[0, 1, 0, 1, BLANK]), Rc(jvar='k', jc=1, Q=[0, 1] * 4 + [run(U, a=1), 1, BLANK]), ('a',)),
  'HEND': (Wc(ivar='i', P=[1, BLANK]), None, ('a',)),
}
if __name__ == '__main__':
    for name in sys.argv[1].split(','):
        s, t, pos = PARTS[name]
        print(name, pl.show(s)); print('   ->', pl.show(t) if t else 'HALT')
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
            print('  OK (%.1fs)' % (time.time() - t0))
            if '-v' in sys.argv: print('\n'.join(mexp.describe(tree)))
        except Exception as e:
            print('  FAIL', str(e)[:500])
