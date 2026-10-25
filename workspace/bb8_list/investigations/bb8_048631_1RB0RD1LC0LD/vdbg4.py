import planner9 as P, fam9 as F
from planner9 import C
import msim, asim
TM = P.TM
def Q1(z, x): return F.ecfg([('100', z), ('001', 1), ('100', x)])
def Q2(z, x): return F.ecfg([('100', z), ('011', 1), ('100', x)])
N = {'z':'z','x':'x'}
T1 = P.make_template(Q1(C(0, z=1), C(0, x=1)), N)[0]
s1 = P.instantiate(T1, {'z': C(3, z=1), 'x': C(6, x=1)})
sc1, got1 = P.drive_until_string2('R1', s1, Q2(C(2, z=1), C(23, x=3)), matchers=[F.m_TL], maxlit=30000)
T2, m2 = P.make_template(got1, N)
print('T2', T2)
s3 = P.instantiate(T2, {'z': C(2), 'x': C(22)})
print('s3', P.show(s3))
print('string s3', P.flat_side(s3[1], {}), '|', P.flat_side(s3[2], {}))
q2 = Q2(C(2), C(22))
print('string Q2', P.flat_side(q2[1], {}), '|', P.flat_side(q2[2], {}))
# planner E-events (flattened) vs macro-sim E-events
pev = []
def m_log(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0:
        pev.append(P.flat_side(L, {}))
    return None
m_log.anytime = True
try:
    P.drive("R3c", s3, None, matchers=[m_log, F.m_TL], verbose=False, maxlit=4000, maxev=400)
except Exception as e:
    print('exc', e)
m = msim.from_blocks(TM, [('100', 2), ('011', 1), ('100', 22)], 'E', 'R', [('100', 1), ('110', 1)])
a = asim.ASim(m)
mev = []
while a.nmacro < 200000 and len(mev) < 25:
    a.step()
    if m.q == 'E' and m.d == 'R' and len(m.R) == 2 and m.R[-1] == [(1,0,0), 1] and m.R[0] == [(1,1,0), 1]:
        s = ''.join(''.join(map(str, b)) * c for b, c in m.L)
        mev.append(s[::-1].rstrip('0')[::-1] if False else s.lstrip('0'))
pset = set(x[::-1].rstrip('0')[::-1] for x in pev)
# planner flat_side of L is stream order (reversed); convert to left-to-right
pl = [x[::-1].lstrip('0') for x in pev]
print('planner events', len(pl), 'macro events', len(mev))
ms = set(mev)
for i, x in enumerate(pl[:40]):
    print(i, 'IN_MACRO' if x in ms else 'not', len(x), x[-60:])
target = '100' * 75 + '001' + '100' * 22
print('target in macro events:', target in ms, ' in planner events:', target in set(pl))
