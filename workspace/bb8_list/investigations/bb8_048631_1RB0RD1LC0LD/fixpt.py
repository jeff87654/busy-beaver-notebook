import sys, pickle
import planner9 as P
import fam9 as F
from planner9 import C, cadd, cconst, cscale
FORM = {'A': F.PA, 'B': F.PB, 'C': F.PC}
NEXT = {'A': 'B', 'B': 'C', 'C': 'A'}
RULE = {'A': (7, 3921), 'B': (6, 3974), 'C': (8, 4004)}   # y decrement, x constant (fam.py params)
OFF = dict(z=1, y=12, x=6)   # planner offsets at round start (template params = var + OFF)

def run_round(ph, tpl, off):
    env = {'z': C(OFF['z'], z=1), 'y': C(OFF['y'], y=1), 'x': C(OFF['x'], x=1)}
    start = P.instantiate(tpl, env)
    fz = cadd(env['z'], cconst(off[0])); fy = cadd(env['y'], cconst(off[1])); fx = cadd(env['x'], cconst(off[2]))
    dy, cx = RULE[ph]
    tz = cadd(fz, cconst(-1)); ty = cadd(fy, cconst(-dy)); tx = cadd(cscale(fx, 27), cconst(cx))
    target = FORM[NEXT[ph]](tz, ty, tx)
    script, got = P.drive_until_string2('R' + ph, start, target, matchers=[F.m_TL])
    assert got is not None, 'no match'
    tnext, mapping = P.make_template(got, {'z': 'z', 'y': 'y', 'x': 'x'})
    offn = []
    for fv, famc in (('z', tz), ('y', ty), ('x', tx)):
        d = cadd(famc, mapping[fv], -1)
        assert not d[1], (fv, famc, mapping[fv])
        offn.append(d[0])
    return start, got, tnext, tuple(offn), mapping

tplA0 = P.make_template(F.PA(C(0, z=1), C(0, y=1), C(0, x=1)), {'z': 'z', 'y': 'y', 'x': 'x'})[0]
tpl, off, ph = tplA0, (0, 0, 0), 'A'
hist = []
for it in range(7):
    start, got, tnext, offn, mapping = run_round(ph, tpl, off)
    print('round', ph, 'off', off, '->', NEXT[ph], 'mapping', {k: P.cstr(v) for k, v in mapping.items()}, 'offn', offn)
    print('   start', P.show(start)[:200])
    print('   end  ', P.show(got)[:200])
    hist.append((ph, tpl, off, tnext, offn))
    tpl, off, ph = tnext, offn, NEXT[ph]
pickle.dump(hist, open('fixpt_hist.pkl', 'wb'))
