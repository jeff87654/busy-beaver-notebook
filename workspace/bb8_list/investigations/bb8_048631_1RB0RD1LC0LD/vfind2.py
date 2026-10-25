import re, sys
import planner9 as P, fam9 as F
from planner9 import C
start = ('A', [P.BLANK], [P.BLANK], '>')
def size(side):
    n = 0
    for t in side:
        if isinstance(t, int): n += 1
        elif P.is_run(t): n += 3 * t[2][0]
    return n
pat = re.compile(r'^((?:100)*)(001|011|00|01)((?:100)*)$')
found = []
def m_look(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0:
        if size(L) > 100000: return None
        s = P.flat_side(L, {})[::-1].lstrip('0')
        m = pat.match(s)
        if m:
            found.append((len(m.group(1)) // 3, m.group(2), len(m.group(3)) // 3))
            if len(found) >= 12: raise StopIteration
    return None
m_look.anytime = True
try:
    P.drive('X', start, None, matchers=[m_look, F.m_TL], verbose=False, maxlit=60000, maxev=50000)
except StopIteration:
    pass
except Exception as e:
    print('exc', repr(e))
for r in found: print(r)
