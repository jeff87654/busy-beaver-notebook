"""B4 search in collapsed semantics over Boolean algebras 2^k (k=2,3), any designated filter, any Q, atoms."""
import sys, itertools
sys.path.insert(0, '..'); import lowprio  # noqa
from collapse import failures
for k in (2, 3):
    nv = 1 << k; top = nv - 1
    I = [tuple(((~a) | b) & top for b in range(nv)) for a in range(nv)]
    N = tuple((~a) & top for a in range(nv))
    # designated sets: principal filters
    Ds = [set(v for v in range(nv) if v & f == f) for f in range(1, nv)] + [{top}]
    cnt = 0
    for D in Ds:
        for Q in itertools.product(range(nv), repeat=nv):
            for eq in range(nv):
                for el in range(nv):
                    bad = failures((I, N, Q, eq, el), D)
                    if bad == {'B4'}:
                        print(k, sorted(D), Q, eq, el, flush=True); cnt += 1
                        if cnt > 3: sys.exit(0)
    print('k', k, 'done', cnt, flush=True)
