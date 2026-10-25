import cands, ngdsl
from modelcheck import *
f = cands.ngA(); lab = ngdsl.greedy_labels(f)
psi = relabel(f[2], lab); ln = lab['n1']
for k in range(4):
    n = ordinal(k)
    print(k, ev(psi, {ln: n}, universe(n)), flush=True)
