import planner9 as P, fam9 as F
from planner9 import C
# concrete cells config: 100^75 001 111 100^19 E> 10011
cfg = F.ecfg([('100', 75), ('001', 1), ('111', 1), ('100', 19)])
print(P.show(cfg)[-120:])
r = F.m_TL(cfg)
print(r[2], r[1][-1][:200])
print(P.show(r[0])[-150:])
print(P.flat_side(r[0][1], {})[::-1].lstrip('0') == '100'*75 + '001' + '100'*22)
cfg2 = F.ecfg([('100', C(75)), ('001', 1), ('111', 1), ('100', C(19))])
print(P.show(cfg2)[-120:])
r = F.m_TL(cfg2)
print(r[2], r[1])
print(P.flat_side(r[0][1], {})[::-1].lstrip('0') == '100'*75 + '001' + '100'*22)
