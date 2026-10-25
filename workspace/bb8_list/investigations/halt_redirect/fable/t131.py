import sys; sys.path.insert(0, '.')
from st import run, fmt, expand
# stage 131 input: prefix + P 4 0 0 1 3 | a=1 | r.   P = 2r_N - 6 (parked), r = current accumulator
for pre in ['9^13 6 24 24 10 0 0 17 10 0 0 17 10 0 0', '9^13 6 5064 5064 10 0 0 5057 10 0 0 5057 10 0 0']:
    for P in [32, 32+2520, 32+5040]:
        for r in [19, 2539, 5059, 7579]:
            toks = expand(pre) + [P, 4, 0, 0, 1, 3]
            o = run(toks, 1, r)
            print(f'pre={pre[:12]}.. P={P} r={r}: {fmt(o)}', flush=True)
