import sys
from msim import *
import asim
TM = sys.argv[1]
FORMS = {
 'Q1': [('100', 'z'), ('001', 1), ('100', 'x')],
 'Q2': [('100', 'z'), ('011', 1), ('100', 'x')],
}
TAIL = [('100', 1), ('110', 1)]
def build(form, z, x):
    left = [(b, z if c == 'z' else x if c == 'x' else c) for b, c in FORMS[form]]
    left = [(b, c) for b, c in left if c]
    return from_blocks(TM, left, 'E', 'R', TAIL)
def match(m):
    if not (m.q == 'E' and m.d == 'R' and len(m.R) == 2 and m.R[-1] == [(1,0,0), 1] and m.R[0] == [(1,1,0), 1]):
        return None
    L = [(''.join(map(str, b)), c) for b, c in m.L]
    for name, f in FORMS.items():
        if len(L) != len(f): continue
        vals = {}; ok = True
        for (b, c), (fb, fc) in zip(L, f):
            if b != fb: ok = False; break
            if isinstance(fc, str): vals[fc] = c
            elif c != fc: ok = False; break
        if ok: return name, vals
    return None
def run(m, maxmacro=2*10**5):
    a = asim.ASim(m)
    try:
        while a.nmacro < maxmacro:
            a.step()
            r = match(m)
            if r: return m.steps, r
    except Halt as h:
        return 'HALT', str(h)[:80]
    return None
for form in sys.argv[2].split(','):
    for z in [int(v) for v in sys.argv[3].split(',')]:
        for x in (22, 23, 24, 25, 70, 71, 72, 73, 100, 101, 102):
            m = build(form, z, x)
            r = run(m)
            print(form, z, x, "->", r, flush=True)
