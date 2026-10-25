import planner9 as P, fam9 as F
from planner9 import C
from tmlit import Sim
TM = P.TM
word_left = '100' * 2 + '011' + '100' * 22
word = word_left + '10011'
s = Sim.from_word(TM, word, len(word_left), 'E', size=1 << 16)
lit = []
while s.steps < 60000:
    if s.state == 4 and s.tape[s.pos] == 1:
        lo, hi = s.bounds()
        right = ''.join(map(str, s.tape[s.pos:hi+1]))
        if right == '10011':
            lit.append(''.join(map(str, s.tape[lo:s.pos])).lstrip('0'))
    if not s.step():
        print('HALT'); break
print('literal E-events', len(lit))
target = '100' * 75 + '001' + '100' * 22
print('target in literal:', target in set(lit), 'at index', lit.index(target) if target in lit else None)
# planner
N = {'z':'z','x':'x'}
T1 = P.make_template(F.ecfg([('100', C(0, z=1)), ('001', 1), ('100', C(0, x=1))]), N)[0]
s1 = P.instantiate(T1, {'z': C(3, z=1), 'x': C(6, x=1)})
sc1, got1 = P.drive_until_string2('R1', s1, F.ecfg([('100', C(2, z=1)), ('011', 1), ('100', C(23, x=3))]), matchers=[F.m_TL], maxlit=30000)
T2, m2 = P.make_template(got1, N)
s3 = P.instantiate(T2, {'z': C(2), 'x': C(22)})
pl = []
def m_log(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0 and len(pl) < 25:
        pl.append((P.flat_side(L, {})[::-1].lstrip('0'), P.show(cfg)[-120:]))
    return None
m_log.anytime = True
try:
    P.drive("R3c", s3, None, matchers=[m_log, F.m_TL], verbose=False, maxlit=3000, maxev=300)
except Exception as e:
    pass
ls = set(lit)
for i, (x, sh) in enumerate(pl):
    print(i, 'LIT' if x in ls else '---', len(x), sh)
print('literal index of planner events:', [lit.index(x) if x in ls else None for x, _ in pl])
for i in range(95, 110):
    x = lit[i]
    print(i, len(x), x[-40:], x[:12])
