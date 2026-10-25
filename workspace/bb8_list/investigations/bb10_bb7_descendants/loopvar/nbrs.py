"""Radius-1 / radius-2 neighbours of a machine (10 states, A..J): every transition (or pair) replaced by every other
value (write 0/1 x move L/R x next state A..J, or undefined '---').  python nbrs.py MACHINE RADIUS [SLOTS] > out.txt
SLOTS: comma-separated transition names (e.g. E0,H0,I1) to restrict the changes; default all 20."""
import itertools, sys
m = sys.argv[1]; rad = int(sys.argv[2])
st = m.split('_'); n = len(st)
vals = ['---'] + [f'{w}{d}{chr(65 + q)}' for w in '01' for d in 'LR' for q in range(n)]
slots = [(i, c) for i in range(n) for c in (0, 1)]
if len(sys.argv) > 3:
    want = set(sys.argv[3].split(','))
    slots = [(i, c) for i, c in slots if f'{chr(65 + i)}{c}' in want]
def get(s, i, c): return s[i][3 * c:3 * c + 3]
def put(s, i, c, v):
    t = list(s); t[i] = t[i][:3 * c] + v + t[i][3 * c + 3:] if c == 0 else t[i][:3] + v; return t
seen = set()
for combo in itertools.combinations(slots, rad):
    choices = [[v for v in vals if v != get(st, i, c)] for i, c in combo]
    for vs in itertools.product(*choices):
        t = st
        for (i, c), v in zip(combo, vs):
            t = put(t, i, c, v)
        x = '_'.join(t)
        if x not in seen:
            seen.add(x); print(x)
