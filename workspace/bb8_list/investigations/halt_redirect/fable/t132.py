import sys; sys.path.insert(0, '.')
from st import run, fmt, expand
pre = '9^13 6 24 24 10 0 0 17 10 0 0 17 10 0 0'
for P in [32, 32+2520, 32+5040]:
    for r in [19, 2539, 5059]:
        toks = expand(pre) + [P, 4, 0, 0, 1, 0]
        o = run(toks, 1, r)
        print(f'P={P} r={r}: {fmt(o)}', flush=True)
