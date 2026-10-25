import re, sys
import planner9 as P, fam9 as F
from planner9 import C
def Q1(z, x): return F.ecfg([('100', z), ('001', 1), ('100', x)])
def Q2(z, x): return F.ecfg([('100', z), ('011', 1), ('100', x)])
N = {'z':'z','x':'x'}
T1 = P.make_template(Q1(C(0, z=1), C(0, x=1)), N)[0]
s1 = P.instantiate(T1, {'z': C(3, z=1), 'x': C(6, x=1)})
sc1, got1 = P.drive_until_string2('R1', s1, Q2(C(2, z=1), C(23, x=3)), matchers=[F.m_TL], maxlit=30000)
T2, m2 = P.make_template(got1, N)
start = P.instantiate(T2, {'z': C(2), 'x': C(6, x=1)}) if sys.argv[1] == 'R3' else ('A', [P.BLANK], [P.BLANK], '>')
def size(side, env):
    n = 0
    for t in side:
        if isinstance(t, int): n += 1
        elif P.is_run(t): n += 3 * P._cnt_at(t[2], env)
    return n
pat = re.compile(r'^((?:100)*)(001|011)((?:100)*)$')
found = []
def m_look(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0:
        res = []
        for env in ({'x': 1000}, {'x': 1003}):
            if size(L, env) > 200000: return None
            s = P.flat_side(L, env)[::-1].lstrip('0')
            m = pat.match(s)
            if not m: return None
            res.append((len(m.group(1)) // 3, m.group(2), len(m.group(3)) // 3))
        found.append((res, P.show(cfg)[:200]))
        if len(found) >= 6: raise StopIteration
    return None
m_look.anytime = True
try:
    P.drive('X', start, None, matchers=[m_look, F.m_TL], verbose=False, maxlit=20000, maxev=5000)
except StopIteration:
    pass
except Exception as e:
    print('exc', repr(e))
for r, sh in found:
    print(r, sh)
