import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
from c7sim import C7, ktword
from trace import show
def evs(n, R, t, maxs=3 * 10**6):
    s = Sim(C7, ktword('11', [1] * n, 1, 3 * R + 2, t), state='B')
    out = []
    while s.steps < maxs:
        if s.q == 'H' and s.t[s.pos] == 0: out.append((s.steps, show(s)))
        if not s.step(): break
        if s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) == s.pos - 1 and len(out) >= 3:
            out.append((s.steps, 'B> ' + show(s))); break
    return out
for t in (0, 2, 4):
    for R in (6, 11):
        for n in (11, 16):
            ev = evs(n, R, t)
            print('t=%d R=%d n=%d #H0=%d' % (t, R, n, len(ev) - 1))
            for e in ev[:1] + ev[-4:]: print('   ', e[0], e[1][:200])
