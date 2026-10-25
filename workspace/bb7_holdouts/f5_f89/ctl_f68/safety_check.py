# safety_check.py: engine runs (D-accelerated) from post-reset states (A=1, all entries >=1, small values); check the
# safety lemma "every event of depth d>=2 has A >= 2d+7" (exact validity needs only A >= d-1).  Values capped (run stops).
import random
def run(L, maxev=3000, cap=10**6):
    A = 1; L = list(L); worst = None; nev = 0; maxd = 0
    while nev < maxev:
        A += 2 * L[0]; L[0] = 0
        if A > cap: break
        j = 1
        while j < len(L) and L[j] == 0: j += 1
        d = j                          # depth (= len for T)
        if d >= 2:
            maxd = max(maxd, d); w = A - (2 * d + 7); worst = w if worst is None else min(worst, w)
        nev += 1
        if j < len(L): L[:j] = [1] * (j - 1) + [A + 3 - j]; L[j] -= 1
        elif len(L) == 1: L = [1] * (A + 4)
        else: L = [1] * (j - 2) + [A + 2 - (j - 1)]
        A = 1
        if max(L) > cap or len(L) > 10**5: break
    return worst, nev, maxd
rng = random.Random(3); W = None; MD = 0; N = 0
for t in range(20000):
    L = [rng.choice([1, 1, 1, 2, 3]) for _ in range(rng.randrange(1, 40))]
    w, n, md = run(L); N += n; MD = max(MD, md)
    if w is not None: W = w if W is None else min(W, w)
print('events', N, 'max depth seen', MD, 'min (A - (2d+7)) over depth>=2 events', W)
