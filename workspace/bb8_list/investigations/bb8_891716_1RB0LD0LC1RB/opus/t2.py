from w891 import *
import itertools
G = lambda **kw: [dict(zip(kw, v)) for v in itertools.product(*kw.values())]
# R3A end segment
sA, tA = R['R3Am']
eA = PS(2, {}, 1, {'r': 1}, 0, {'k': 1})
print('A start->P1', chk(sA, PS(2, {'k': 1}, 1, {'k': 1, 'r': 1}, 0, {}), G(k=range(4), r=range(4), y=range(3))))
print('A end', chk(eA, tA, G(k=range(4), r=range(4), y=range(3))))
sB, tB = R['R3Bm']
print('B start->P1', chk(sB, PS(3, {'c': 1}, 1, {'c': 1}, 0, {}), G(c=range(5), y=range(3))))
print('B end', chk(PS(3, {}, 1, {}, 0, {'c': 1}), tB, G(c=range(5), y=range(3))))
sC, tC = R['R3Cm']
print('C start->P1', chk(sC, PS(4, {'c': 1, 'm': 1}, 1, {'c': 1}, 0, {}), G(c=range(5), m=range(4), y=range(3))))
print('C end', chk(PS(4, {'m': 1}, 1, {}, 0, {'c': 1}), tC, G(c=range(5), m=range(4), y=range(3))))
