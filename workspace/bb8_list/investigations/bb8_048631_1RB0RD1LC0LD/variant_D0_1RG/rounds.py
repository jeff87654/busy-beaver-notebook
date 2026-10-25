"""Fixed-point family templates and the three round scripts (planner9)."""
import sys, pickle
import planner9 as P
import fam9 as F
from planner9 import C, cadd, cconst, cscale
FORM = {'A': F.PA, 'B': F.PB, 'C': F.PC}
NEXT = {'A': 'B', 'B': 'C', 'C': 'A'}
RULE = {'A': (7, 3921), 'B': (6, 3974), 'C': (8, 4004)}   # y decrement, x constant (fam.py params)
OFF = dict(z=1, y=12, x=6)
NAMES = {'z': 'z', 'y': 'y', 'x': 'x'}

def run_round(ph, tpl, znew=None):
    env = {'z': C(OFF['z'], z=1), 'y': C(OFF['y'], y=1), 'x': C(OFF['x'], x=1)}
    start = P.instantiate(tpl, env)
    fz, fy, fx = env['z'], env['y'], env['x']
    dy, cx = RULE[ph]
    tz = cadd(fz, cconst(-1)); ty = cadd(fy, cconst(-dy)); tx = cadd(cscale(fx, 27), cconst(cx))
    target = FORM[NEXT[ph]](tz, ty, tx)
    script, got = P.drive_until_string2('R' + ph, start, target, matchers=[F.m_TL])
    assert script is not None, 'no match'
    tnext, mapping = P.make_template(got, NAMES)
    for fv, famc in (('z', tz), ('y', ty), ('x', tx)):
        assert mapping[fv] == famc, (fv, mapping[fv], famc)
    return start, script, got, tnext

def fixed_point():
    tpl = P.make_template(F.PA(C(0, z=1), C(0, y=1), C(0, x=1)), NAMES)[0]
    ph = 'A'
    seen = {}
    for it in range(12):
        start, script, got, tnext = run_round(ph, tpl)
        key = (ph, repr(tpl))
        if key in seen:
            break
        seen[key] = (tpl, start, script, got, tnext)
        tpl, ph = tnext, NEXT[ph]
    # collect the cycle starting at the repeated key
    cyc = {}
    for ph2 in 'ABC':
        pass
    return seen

if __name__ == '__main__':
    seen = fixed_point()
    # templates: take the last occurrence per phase whose start template reappears
    T = {}
    SC = {}
    for (ph, k), v in seen.items():
        T[ph] = v[0]; SC[ph] = v
    # verify closure: T[NEXT[ph]] == tnext of T[ph]
    for ph in 'ABC':
        tpl, start, script, got, tnext = SC[ph]
        print(ph, 'closure ok' if repr(tnext) == repr(T[NEXT[ph]]) else 'CLOSURE MISMATCH',
              'ops', len(script), 'literal', sum(len(o[1]) for o in script if o[0] == 'lits'))
    pickle.dump(SC, open('rounds.pkl', 'wb'))
    pickle.dump(P.LEMMAS, open('lemmas.pkl', 'wb'))
