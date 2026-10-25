import planner9 as P, fam9 as F
from planner9 import C
print(P.TM)
def Q1(z, x): return F.ecfg([('100', z), ('001', 1), ('100', x)])
def Q2(z, x): return F.ecfg([('100', z), ('011', 1), ('100', x)])
T1 = P.make_template(Q1(C(0, z=1), C(0, x=1)), {'z':'z','x':'x'})[0]
s1 = P.instantiate(T1, {'z': C(3, z=1), 'x': C(6, x=1)})
tgt = Q2(C(2, z=1), C(23, x=3))
cnt = [0]
def m_log(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0:
        cnt[0] += 1
        if cnt[0] < 40: print('EV', P.show(cfg)[:220])
    return None
m_log.anytime = True
print('target', P.show(tgt))
try:
    sc, got = P.drive('R1', s1, lambda c: c[0]==tgt[0] and c[3]==tgt[3] and P.same_string(c, tgt), matchers=[m_log, F.m_TL], verbose=False, maxlit=30000)
    print('END', sc[-1] if sc else None, P.show(got)[:300])
except Exception as e:
    print('EXC', e)
