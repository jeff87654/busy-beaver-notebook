import sys, itertools, collections
sys.path.insert(0, '..'); import lowprio  # noqa
from collapse import failures
k=2; nv = 1 << k; top = nv - 1
I = [tuple(((~a) | b) & top for b in range(nv)) for a in range(nv)]
N = tuple((~a) & top for a in range(nv))
Ds = [set(v for v in range(nv) if v & f == f) for f in range(1, nv)]
C = collections.Counter()
for D in Ds:
    for Q in itertools.product(range(nv), repeat=nv):
        for eq in range(nv):
            for el in range(nv):
                bad = failures((I, N, Q, eq, el), D)
                if 'B4' in bad: C[tuple(sorted(bad))] += 1
for k_, v in C.most_common(15): print(v, k_)
