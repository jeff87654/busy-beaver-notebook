import planner9 as P, fam9 as F, time
from planner9 import C
def Q1(z, x): return F.ecfg([('100', z), ('001', 1), ('100', x)])
def Q2(z, x): return F.ecfg([('100', z), ('011', 1), ('100', x)])
N = {'z':'z','x':'x'}
T1 = P.make_template(Q1(C(0, z=1), C(0, x=1)), N)[0]
s1 = P.instantiate(T1, {'z': C(3, z=1), 'x': C(6, x=1)})
t = time.time()
sc1, got1 = P.drive_until_string2('R1', s1, Q2(C(2, z=1), C(23, x=3)), matchers=[F.m_TL], maxlit=30000)
print('R1', time.time() - t, P.show(got1)); T2, m2 = P.make_template(got1, N); print(m2)
s2 = P.instantiate(T2, {'z': C(3, z=1), 'x': C(6, x=1)})
t = time.time()
sc2, got2 = P.drive_until_string2('R2', s2, Q1(C(1, z=1), C(28, x=3)), matchers=[F.m_TL], maxlit=30000)
print('R2', time.time() - t, sc2 is not None, P.show(got2)[:300])
T1b, m1 = P.make_template(got2, N)
print('fixed', repr(T1b) == repr(T1))
s3 = P.instantiate(T2, {'z': C(2), 'x': C(6, x=1)})
t = time.time()
try:
    sc3, got3 = P.drive_until_string2('R3', s3, Q1(C(27, x=3), C(22)), matchers=[F.m_TL], maxlit=50000)
    print('R3', time.time() - t, sc3 is not None, P.show(got3)[:300])
except Exception as e:
    print('R3 EXC', e, time.time() - t)
s0 = ('A', [P.BLANK], [P.BLANK], '>')
t = time.time()
try:
    sc0, got0 = P.drive_until_string2('INIT', s0, Q1(C(3), C(22)), matchers=[F.m_TL], maxlit=50000)
    print('INIT', time.time() - t, sc0 is not None, P.show(got0)[:300])
except Exception as e:
    print('INIT EXC', e, time.time() - t)
