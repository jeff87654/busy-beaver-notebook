"""rebuild_usage.py LABEL...: slot reads during the R4 path from K(0^n;0;b) (b=1) to the first read of an
undefined slot or the rebuilt K-moment; prints per-slot counts and the order of first reads"""
import sys
from eng import *
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
for lbl in sys.argv[1:]:
    m, t, n = BASES[lbl][0], BASES[lbl][1], int(BASES[lbl][2]); T = parse_tmpl(t)
    w = '0000' + kword(T, [0] * n, 0, 1) + '0'
    r = run_to_event(m, w, len(w) - 1, T['Q'], 5_000_000, T, minlen=len(w) + 6 + 12)
    s = Sim.from_word(m, w, len(w) - 1, T['Q'], size=1 << 18); s.usage = {}; order = []
    while s.steps < r[1]:
        k = 'ABCDEFGHIJ'[s.state] + str(s.tape[s.pos])
        if k not in order: order.append(k)
        if not s.step(): break
    print(lbl, r[0], r[1], 'first-read order:', ' '.join(order), '| counts:', ' '.join(f"{'ABCDEFGHIJ'[q]}{c}:{v}" for (q, c), v in sorted(s.usage.items())))
