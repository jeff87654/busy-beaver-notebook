from solve_rounds import load, classify_cell
from solve_rounds2 import solve2
import sys
for path in sys.argv[1:]:
    for cat, fam, tm, tab in load(path):
        kmax = max(tab)
        res = solve2(tab, kmax)[0]
        if res != 'NOFIT':
            continue
        cls = {k: classify_cell(tab[k]) for k in range(1, kmax + 1)}
        s = ''.join(cls[k][0][0] for k in range(1, kmax + 1))
        hk = [k for k in range(40, kmax + 1) if cls[k][0] == 'H']
        print(('H40+' if hk else 'noH40'), fam, tm)
        print('   kinds k=1..%d: %s' % (kmax, s))
        print('   dL k=30..72:', [cls[k][1] if cls[k][0] == 'K' else cls[k][0] for k in range(30, kmax + 1)])
        print('   I  k=30..72:', ''.join(str(cls[k][2]) if cls[k][0] == 'K' else '.' for k in range(30, kmax + 1)))
