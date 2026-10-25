"""kgcmp.py: which k-gram contexts occur in the special stages (exhaustion, left event/repack) but in no normal stage"""
import sys, pickle
sys.path.insert(0, '.')
from kg import kgrams
M = sys.argv[1] if len(sys.argv) > 1 else '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_0RG1LD_1RH1LG_1LC0RG_1RJ1LA_1LI---'
KM = 6
normal = ['6^16 8 1^30 1 2', '6^16 5 3 1^30 1 19', '6^16 5 0 1^30 1 19', '6^14 4 2 1^40 1 19', '6^14 1 44 1^40 1 2',
          '6^14 1 41 3 1^40 1 19', '6^14 1 41 0 1^40 1 19', '6^4 4 2 1^20 1 19', '6^4 1 41 3 1^20 1 19', '6^4 1 41 0 1^20 1 19',
          '6^2 1 41 0 1^20 1 19', '6^2 1 41 0 1^5 1 19', '6^2 4 2 1^5 1 19', '6^2 1 41 3 1^5 1 19',
          '6^2 4 2 1^20 1 2539', '6^2 1 41 3 1^20 1 2539', '6^2 1 41 0 1^20 1 2539', '6^2 1 5081 0 1^20 1 19', '6^4 4 2546 1^62 1 1',
          '6^2 4 26 1^20 1 1', '6^4 4 26 1^3 1 1', '6^2 1 41 0 43 1^10 1 1', '6^2 1 41 0 43 1^3 1 1']
special = ['1 41 0 1^20 1 19', '1 41 0 1^5 1 19', '7 1^30 1 1', '1^30 1 19', '1^5 1 19', '1 5081 0 1^20 1 19']
N = {}
for c in normal:
    rc = 10**6 if c.endswith(' 1 1') else 600
    end, d = kgrams(M, c, kmax=KM, rcap=rc)
    print('normal', c, end, len(d), flush=True)
    for k, v in d.items():
        N.setdefault(k, 0); N[k] += v[0]
S = {}
for c in special:
    end, d = kgrams(M, c, kmax=KM)
    print('special', c, end, len(d), flush=True)
    for k, v in d.items():
        if k not in N:
            S.setdefault(k, []).append((c, v))
pickle.dump((N, S), open('logs/kgcmp.pkl', 'wb'))
for k in range(2, KM + 1):
    u = [(g, S[g]) for g in S if g[0] == k]
    print(f'k={k}: {len(u)} unique special contexts')
    for g, occ in sorted(u, key=lambda x: x[1][0][1][1])[:40]:
        print('  ', ','.join(g[1]), [(c, v) for c, v in occ])
