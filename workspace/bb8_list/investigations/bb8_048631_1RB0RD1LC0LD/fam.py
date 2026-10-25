"""Checkpoint families (block-3 alignment, left-to-right), exploration tool."""
import re, sys
from msim import *
import asim
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
TAIL = [('100', 1), ('110', 1)]
FORMS = {
 'PA': [('001', 'z'), ('000', 1), ('011', 1), ('110', 1), ('010', 'y'), ('000', 1), ('111', 1), ('001', 'x'), ('000', 1), ('011', 1), ('111', 3), ('001', 1), ('100', 1)],
 'PB': [('100', 'z'), ('001', 1), ('111', 1), ('001', 'y'), ('000', 1), ('011', 1), ('001', 'x'), ('000', 1), ('011', 1), ('111', 14), ('001', 1), ('100', 1)],
 'PC': [('010', 'z'), ('000', 1), ('111', 1), ('100', 'y'), ('001', 'x'), ('000', 1), ('011', 1), ('111', 47), ('001', 1), ('100', 1)],
}
def build(form, **v):
    left = []
    for b, c in FORMS[form]:
        left.append((b, v[c] if isinstance(c, str) else c))
    left = [(b, c) for b, c in left if c != 0]
    return from_blocks(TM, left, 'E', 'R', TAIL)

def match(m):
    if not (m.q == 'E' and m.d == 'R' and len(m.R) == 2 and m.R[-1] == [(1,0,0), 1] and m.R[0] == [(1,1,0), 1]):
        return None
    L = [(''.join(map(str, b)), c) for b, c in m.L]
    for name, f in FORMS.items():
        if len(L) != len(f): continue
        vals = {}
        ok = True
        for (b, c), (fb, fc) in zip(L, f):
            if b != fb: ok = False; break
            if isinstance(fc, str): vals[fc] = c
            elif c != fc: ok = False; break
        if ok: return name, vals
    return None

def run(m, maxmacro=10**6, verbose=False, stop_first=True):
    a = asim.ASim(m)
    out = []
    try:
        while a.nmacro < maxmacro:
            a.step()
            r = match(m)
            if r:
                out.append((m.steps, r))
                if verbose: print(m.steps, r, flush=True)
                if stop_first: return out, None
    except Halt as h:
        return out, ('HALT', str(h), m.show(), m.steps)
    return out, ('TIMEOUT', m.show())

if __name__ == '__main__':
    form = sys.argv[1]; z, y, x = map(int, sys.argv[2:5]); n = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    m = build(form, z=z, y=y, x=x)
    a = asim.ASim(m)
    cnt = 0
    try:
        while cnt < n:
            a.step()
            r = match(m)
            if r:
                print(m.steps, r, flush=True); cnt += 1
    except Halt as h:
        print('HALT', h, m.show())
