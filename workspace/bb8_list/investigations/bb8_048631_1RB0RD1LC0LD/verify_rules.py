"""Check round and ending rules with the PLAIN macro simulator (msim, no heuristic acceleration)."""
import sys
from fam import *
RULE = {
 ('PA', 'reg'): lambda z, y, x: ('PB', z - 1, y - 7, 27 * x + 3921),
 ('PB', 'reg'): lambda z, y, x: ('PC', z - 1, y - 6, 27 * x + 3974),
 ('PC', 'reg'): lambda z, y, x: ('PA', z - 1, y - 8, 27 * x + 4004),
 ('PA', 'end'): lambda z, y, x: ('PB', y - 7, 27 * x + 3918, 141),
 ('PB', 'end'): lambda z, y, x: ('PC', y - 7, 27 * x + 3973, 140),
 ('PC', 'end'): lambda z, y, x: ('PA', y - 8, 27 * x + 3999, 143),
}
def run_plain(m, maxmacro):
    n = 0
    while n < maxmacro:
        m.step(); n += 1
        r = match(m)
        if r: return m.steps, r
    return None
accel = len(sys.argv) > 1 and sys.argv[1] == 'accel'
bad = 0; cnt = 0
cases = []
for form in ('PA', 'PB', 'PC'):
    for x in list(range(4, 16)) + [50, 51, 52]:
        for y in (8, 9, 10, 11, 20, 21, 22, 23):
            for z in (0, 1, 2):
                cases.append((form, z, y, x))
for form, z, y, x in cases:
    kind = 'end' if z == 0 else 'reg'
    want = RULE[(form, kind)](z, y, x)
    if z == 0 and y < 9: continue
    m = build(form, z=z, y=y, x=x)
    if accel:
        out, err = run(m, 10**6)
        got = None if err else out[0]
    else:
        got = run_plain(m, 3 * 10**6)
    cnt += 1
    if got is None:
        print('NO MATCH', form, z, y, x); bad += 1; continue
    st, (f2, v) = got
    g = (f2, v['z'], v['y'], v['x'])
    if g != want:
        bad += 1; print('MISMATCH', form, z, y, x, 'got', g, 'want', want)
print('checked', cnt, 'bad', bad)
