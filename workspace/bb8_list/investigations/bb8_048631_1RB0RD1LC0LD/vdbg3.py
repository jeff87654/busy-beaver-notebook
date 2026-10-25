import planner9 as P, fam9 as F, time
from planner9 import C
def Q1(z, x): return F.ecfg([('100', z), ('001', 1), ('100', x)])
def Q2(z, x): return F.ecfg([('100', z), ('011', 1), ('100', x)])
N = {'z':'z','x':'x'}
T1 = P.make_template(Q1(C(0, z=1), C(0, x=1)), N)[0]
s1 = P.instantiate(T1, {'z': C(3, z=1), 'x': C(6, x=1)})
sc1, got1 = P.drive_until_string2('R1', s1, Q2(C(2, z=1), C(23, x=3)), matchers=[F.m_TL], maxlit=30000)
T2, m2 = P.make_template(got1, N)
s3 = P.instantiate(T2, {'z': C(2), 'x': C(6, x=1)})
print('R3 start', P.show(s3))
n = [0]
def m_log(cfg):
    n[0] += 1
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0 and n[0] < 1200:
        print(n[0], P.show(cfg)[:250], P.same_string(cfg, Q1(C(27, x=3), C(22))), flush=True)
    return None
m_log.anytime = True
try:
    sc3, got3 = P.drive('R3', s3, None, matchers=[m_log, F.m_TL], verbose=False, maxlit=20000)
    print('R3 END', P.show(got3)[:300])
except Exception as e:
    print('R3 EXC', e)
