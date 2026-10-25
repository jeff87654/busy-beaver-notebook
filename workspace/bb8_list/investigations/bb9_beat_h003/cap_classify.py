"""Cap-invariance classification.  The collapse macros replace a huge unary accumulator u by a small
u_cap == u (mod 12).  A table cell is trustworthy only if the gadget outcome does not depend on the
magnitude of u: we recompute every cell with u_cap shifted by CAPX in {12, 24, 120} and demand that
(kind, dL, I) is unchanged.  Cells whose dL moves with CAPX mean the rebuilt list length contains a
term ~u/2 (the collapsed accumulator is copied into the next round's digit list), so dL is only
known modulo a small number and the residue solver cannot be applied."""
import sys
from collections import Counter
from solve_rounds import load, classify_cell
import solve_rounds2 as S

def loadmap(path):
    return {tm: tab for cat, fam, tm, tab in load(path)}, {tm: fam for cat, fam, tm, tab in load(path)}

groups = [('capA', 72), ('capS1', 72), ('capS2', 72), ('capN', 200)]
caps = [0, 12, 24, 120]
out = open('cap_classify.out.txt', 'w')
stats = Counter()
for g, kmax in groups:
    maps = {}
    fams = None
    for c in caps:
        m, f = loadmap('%s_%d.txt' % (g, c))
        maps[c] = m
        fams = fams or f
    for tm, tab0 in maps[0].items():
        if classify_cell(tab0[20])[0] != 'K':
            continue
        nonrob = []
        for k in tab0:
            vals = set()
            for c in caps:
                t = maps[c].get(tm, {}).get(k)
                if t is None:
                    vals.add(None); continue
                vals.add((t[0].upper(), t[1], t[2], t[3], t[4]))
            if len(vals) > 1:
                nonrob.append(k)
        tail_nonrob = [k for k in nonrob if k >= 12]
        rob20 = 20 not in nonrob
        res = S.solve2(tab0, max(tab0))
        tag = 'ROBUST' if not tail_nonrob else ('SENSITIVE')
        stats[(g, tag, res[0] if res[0] != 'HALT' else 'HALT_R%d' % res[1])] += 1
        out.write('%-9s %-6s k20rob=%s %-12s R=%d %-22s %s nonrob_tail=%d first=%s\n' % (
            tag, g, rob20, res[0], res[1], fams[tm], tm, len(tail_nonrob), tail_nonrob[:10]))
out.write('\n')
for k, v in sorted(stats.items()):
    out.write('%s %d\n' % (k, v))
    print(k, v)
