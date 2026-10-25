"""Exact cycle check from c_end(q, r): simulate, and record the full configuration (state, head, tape) every step
once the head stays inside a window; a repeated configuration proves non-halting (the run is periodic).
Usage: python cyclecheck.py MACHINE q r [maxsteps]"""
import sys
from cend import c_end
m, q, r = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
maxs = int(sys.argv[4]) if len(sys.argv) > 4 else 2000000
rows = m.split('_')
T = {}
for si, row in enumerate(rows):
    for b in range(2):
        c = row[3 * b:3 * b + 3]
        if c[0] != '-':
            T[(chr(65 + si), b)] = (int(c[0]), 1 if c[1] == 'R' else -1, c[2])
tape, h, s = c_end(q, r)
t = dict((i, 1) for i, ch in enumerate(tape) if ch == '1')
seen = {}
for step in range(maxs):
    sym = t.get(h, 0)
    if (s, sym) not in T:
        print('HALT', step, s, sym); sys.exit()
    if step % 1 == 0 and step > 1000:
        key = (s, h, frozenset(t))
        if key in seen:
            print(f'CYCLE: configuration at step {step} repeats step {seen[key]} (period {step - seen[key]}), head {h}')
            sys.exit()
        seen[key] = step
    w, d, ns = T[(s, sym)]
    if w:
        t[h] = 1
    else:
        t.pop(h, None)
    h += d; s = ns
print('no cycle within', maxs)
