from explore_rules import *
import sys

cfg = gamma(X, J, Z, r)
ncross = int(sys.argv[1]) if len(sys.argv) > 1 else 7
for i in range(ncross):
    while True:
        try:
            head(cfg)
        except Stuck:
            break
        cfg = step(cfg)
    cfg, nm = apply_crossing(cfg)
    print(nm)
print('after crossings:', show(cfg))
n = 0
while True:
    try:
        head(cfg)
    except Stuck:
        break
    q, L, s, R = triple(cfg)
    if L == [BLANK] or tuple(L) == (BLANK,):
        print(n, q, s, ' '.join(tok_str(t, False) for t in R))
    cfg = step(cfg)
    n += 1
print('stuck', n, show(cfg))
