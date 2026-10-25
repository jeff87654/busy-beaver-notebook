"""Event specs for the round-2 end of T12a (from Per L K 3 n a to the halt). Same conventions as evs12.py."""
from evs12 import *
def raw(*bits):
    """raw cells, left-to-right"""
    return list(reversed(bits))
# the raw cells left by E20 (left-to-right): 1 1 1 00 1 00000 1 00000 1 00000
R20 = raw(1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0)
EVE = {}
# E20: Per L (4 + K) 3 n a -> [L 2^K R20 2 2 0 | a 1^3 0 1^n | 6]
EVE['E20'] = (WL(TWOS(K=1), tok(2), tok(2), tok(2), tok(2), tok(5), ones(3), Z(), Z(), tok(2), ONES(n=1), Z(), tok(0, a=1)),
              WL(TWOS(K=1), R20, tok(2), tok(2), Z(), tok(0, a=1), ones(3), Z(), ONES(n=1), Z(), tok(6)))
def shift(name, **sh):
    S, T = EVE[name][:2]
    for v, c in sh.items():
        S = engine.subst(S, v, ((v, 1),), c)
        T = engine.subst(T, v, ((v, 1),), c) if T is not None else None
    EVE[name] = (S, T) + tuple(EVE[name][2:])
shift('E20', a=2)
# the depth list becomes blocks D3 D2 D0, one per event (CONV0 once, then CONV z+1 -> z), then Z0, Z1
EVE['CONV0'] = (WL(tok(7, a=1), ones(3), Z(), ONES(n=1), ones(1), Z(), tok(6)),
                WL(tok(0, a=1), tok(2), Z(), tok(10), ones(3), Z(), ONES(n=1), Z(), tok(6)))
EVE['CONV'] = (WL(tok(10), ones(3), Z(), ONES(z=1), ones(1), Z(), tok(6)),
               WL(tok(3), tok(2), Z(), tok(10), ones(3), Z(), ONES(z=1), Z(), tok(6)))
EVE['Z0'] = (WL(tok(10), ones(3), Z(), Z(), tok(6)), WL(tok(7), tok(6), Z(), Z(), tok(8)))
EVE['Z1'] = (WL(tok(7), tok(6), Z(), Z(), tok(8)), WL(tok(3), tok(2), Z(), tok(10), ones(3), Z(), tok(4)))
BLK = (1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1)            # D3 D2 D0 (stream order: D0 nearest)
def BLOCKS(c, **v):
    """(D3 D2 D0)^(c + 6 v)"""
    out = list(BLK) * c
    if v:
        out.append(run(BLK * 6, **v))
    return out
def EAT_START(r):
    return WL(TWOS(K=1), R20, tok(2), tok(2), Z(), tok(0, x=1), tok(2), Z(), BLOCKS(r, j=1), ones(4), Z(), tok(0, A=1))
for _r in range(6):
    EVE['EAT%d' % _r] = (EAT_START(_r), None)
from vspec import vs
# EAT: [L 2^(K+6) R20 2 2 0 X 2 0 (3 2 0)^(r + 6 + 6 j) 1^4 | A]; the leftmost r blocks, then j units of 6, then 6
B6 = '3 2 0 3 2 0 3 2 0 3 2 0 3 2 0 3 2 0'
EAT_IN = 'L 2^{K} 2^6 0 0 0 z2 0 z5 0 z5 0 z5 2 2 0 %s 2 0 ' + '%s' + ' [' + B6 + ']^{j} ' + B6 + ' 1^4 0 T{0,A}'
UNIT = '0 9 z2 0^6 z2 0^3 z4 4 9 0 1^4'
UNIT_O = '0^3 z4 4 9 0 1^4 0 9 z2 0^6 z2'
LEFT_E = 'L 2^{K} 1 T{24,x} 0^6 z2 0 z5 0 z4 4 9 0 1^2 [' + UNIT + ']^{j} 0 9 z2 0^6 z2 '
LEFT_O = 'L 2^{K} 2^6 0 0 0 z2 0 z5 0 z5 0 z5 2 2 0 T{0,x} 4 1^2 3 0^3 8 1^4 0 9 z2 0^6 z2 [' + UNIT_O + ']^{j} '
TAIL = {0: '0 z2 0 z2 2 4 0 T{0,A} 1^3 0 1^3 0 6',
        1: '0^3 z4 10 1^5 0 2 0 T{3,A} 0 1^3 0 6',
        2: '0^3 z4 4 9 0 1^6 2 1^2 0^3 1 2 T{3,A} 0 1^3 0 6'}
for _r in range(6):
    EVE['EAT%d' % _r] = (vs(EAT_IN % ('T{9,x}', ('3 2 0 ' * _r).strip())),
                         vs((LEFT_O if _r % 2 else LEFT_E) + TAIL[_r // 2]))
    shift('EAT%d' % _r, A=4)
# ---- continuations
# class 0/1: the depth-3 list is converted again (CONV0, CONV x2, Z0, Z1, CLR), then the 3-block eat SM3
EVE['SM3'] = (vs('L 2 4 0 T{9,x} 2 0 3 2 0 3 2 0 3 2 0 1^4 0 T{4,A}'),
              vs('L 2 4 0 T{0,x} 6 2 0 2 1 3 1^5 0 2 0 T{7,A} 0 1^3 0 6'))
# classes 0-3: the accumulator A = 40 + 9 y becomes y junk units, then F24, CLR (d=2 at depth 3), HALT1
EVE['F23'] = (vs('L 1^5 0 2 0 T9{43,y} 0 1^3 0 6'),
              vs('L 1^2 0 2 0^2 z2 1 3 z2 0 z2 0 z2 0 z4 0 z5 3 0^6 z2 0 z3 1 z3 [2 z2 0 z2 0^4 z4]^{y} 4 3 1^2 0 1^3 8 1 0 1^2 0 6'))
EVE['F24'] = (vs('L 1^3 8 1 0 1^2 0 6'), vs('L 1^2 0^3 z2 0 z5 0 z4 7 1^3 0 4'))
EVE['HALT1'] = (vs('L 4 3 1^2 0 1^2 0^3 z2 0 z5 0 z4 1^4 0 T{0,A}'), None)
# classes 4/5: A = 3 a + 1
EVE['G1'] = (vs('L 1^6 2 1^2 0^3 1 2 T3{4,a} 0 1^3 0 6'), vs('L 1^6 2 1^2 0^5 8 [1 1]^{a} 1^6 0 4'))
EVE['G2'] = (vs('L 4 9 0 1^6 2 1^2 0^5 2 1^{z} 0 T{0,B}'), vs('L 0 2 0 3 1^11 0 2 T{4,B} 1 0 1^{z} 0 6'))
EVE['G3'] = (vs('L 0 2 0 3 1^11 0 2 T3{5,b} 1 0 1^{z} 0 6'), vs('L 0 2 0 3 1^11 0 1 0^2 z2 [0 z5]^{b} 0 z4 7 1^{z} 1 0 4'))
EVE['HALT2'] = (vs('L 0 1 0^2 z2 [0 z5]^{b} 0 z4 1^{z} 1^2 0 T{0,C}'), None)
shift('HALT2', b=2, z=2, C=4)
