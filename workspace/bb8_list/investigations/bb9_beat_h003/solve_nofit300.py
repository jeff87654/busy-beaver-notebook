import sys
import solve_rounds2 as S
from solve_rounds import load, classify_cell

orig_fit = S.fit
S.fit = lambda cls, kmax: orig_fit(cls, kmax, kmin=20, pmax=95)
for cat, fam, tm, tab in load(sys.argv[1]):
    kmax = max(tab)
    res, r, traj, per = S.solve2(tab, kmax)
    cls = {k: classify_cell(tab[k]) for k in range(1, kmax + 1)}
    hk = [k for k in range(100, kmax + 1) if cls[k][0] == 'H']
    xs = sum(1 for k in range(100, kmax + 1) if cls[k][0] not in ('H', 'K'))
    print('%-10s R=%-3d %-14s %s fit=%s H100+=%d X100+=%d traj=%s' % (res, r, fam, tm, per, len(hk), xs,
          ' '.join('R%d(s=%d,I=%d)%s' % t for t in traj)))
