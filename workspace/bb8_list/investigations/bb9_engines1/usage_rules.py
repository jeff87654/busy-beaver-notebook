"""slot usage of a base during the champion clearing (R1-R3) only: from K([1,0,1]; 2; 1) run 3e5 steps
(no exhaustion happens in that time; checked: no undefined read)."""
import sys
from eng import *
for line in open(sys.argv[1]):
    f = line.split()
    if not f or f[0].startswith('#'): continue
    lbl, m, t = f[0], f[1], f[2]
    T = parse_tmpl(t)
    w = '0000' + kword(T, [1, 0, 1], 2, 1) + '0'
    s = Sim.from_word(m, w, len(w) - 1, T['Q'], size=1 << 18); s.usage = {}
    ok = True
    while s.steps < 300000:
        if not s.step(): ok = False; break
    used = sorted('ABCDEFGHIJ'[q] + str(c) for (q, c) in s.usage)
    allslots = ['ABCDEFGHIJ'[q] + str(c) for q in range(m.count('_') + 1) for c in (0, 1)]
    print(lbl, 'halted!' if not ok else '', 'unused-in-clearing:', ' '.join(x for x in allslots if x not in used))
