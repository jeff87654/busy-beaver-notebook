"""Endings (z = 0), the y = 4 ending and the initial segment, with planner9 on the fixed-point templates."""
import sys, pickle
import planner9 as P
import fam9 as F
from planner9 import C, cadd, cconst, cscale
SC = pickle.load(open('rounds.pkl', 'rb'))
P.LEMMAS.update(pickle.load(open('lemmas.pkl', 'rb')))
T = {ph: SC[ph][0] for ph in 'ABC'}
FORM = {'A': F.PA, 'B': F.PB, 'C': F.PC}
NEXT = {'A': 'B', 'B': 'C', 'C': 'A'}
END = {'A': (7, 3918, 141), 'B': (7, 3973, 140), 'C': (8, 3999, 143)}   # new z = y - d, new y = 27x + c, new x
OY, OX = 20, 6
out = {}

def finish(name, start, target_string, exp):
    script, got = P.drive_until_string2(name, start, target_string, matchers=[F.m_TL], maxev=200000, maxlit=3000000)
    assert script is not None, name
    r = P.normalize_cfg_to(got, exp)
    assert r is not None, name
    cfg2, texts = r
    assert cfg2 == exp
    script = script[:-1] + [('coq', t) for t in texts] + [('stop',)]
    lit = sum(len(o[1]) for o in script if o[0] == 'lits')
    print(name, 'ops', len(script), 'lit', lit, 'norm', len(texts))
    return (start, script, exp)

for ph in 'ABC':
    env = {'z': C(0), 'y': C(OY, y=1), 'x': C(OX, x=1)}
    start = P.instantiate(T[ph], env)
    d, c, nx = END[ph]
    tz = cadd(env['y'], cconst(-d)); ty = cadd(cscale(env['x'], 27), cconst(c)); tx = C(nx)
    target = FORM[NEXT[ph]](tz, ty, tx)
    exp = P.instantiate(T[NEXT[ph]], {'z': tz, 'y': ty, 'x': tx})
    out['E' + ph] = finish('E' + ph, start, target, exp) + ((tz, ty, tx),)
# y = 4 ending: PA(z+5, 4, x) -> PC(z+1, 27x+3922, 140)
env = {'z': C(5, z=1), 'y': C(4), 'x': C(OX, x=1)}
start = P.instantiate(T['A'], env)
tz, ty, tx = C(1, z=1), cadd(cscale(env['x'], 27), cconst(3922)), C(140)
target = F.PC(tz, ty, tx)
exp = P.instantiate(T['C'], {'z': tz, 'y': ty, 'x': tx})
out['Y4'] = finish('Y4', start, target, exp) + ((tz, ty, tx),)
# initial segment: blank -> PA(216, 214, 143)
start = ('A', [P.BLANK], [P.BLANK], '>')
target = F.PA(C(216), C(214), C(143))
exp = P.instantiate(T['A'], {'z': C(216), 'y': C(214), 'x': C(143)})
out['INIT'] = finish('INIT', start, target, exp) + ((C(216), C(214), C(143)),)
pickle.dump(out, open('endings.pkl', 'wb'))
pickle.dump(P.LEMMAS, open('lemmas2.pkl', 'wb'))
