# cobound.py : is the parked-count change a(L mod 5) a 5-adic coboundary of the cascade map g mod 5?
# i.e. does f: Z/5^j -> GF(5) exist with f(g(L)) - f(L) = a(L mod 5) (mod 5) for all L mod 5^(j+1)?
# If yes, P + f(L) mod 5 is invariant along the orbit and rho at the key is forced.
C = {0: -100, 1: 32, 2: -46, 3: -64, 4: -52}; A = {0: 3, 1: 11, 2: 4, 3: 6, 4: 6}
def g(L): return (3 * L + C[L % 5]) // 5
def solve(rows, n, p=5):
    # rows: list of (coeff dict, rhs); gaussian elimination mod p; returns True if consistent
    piv = {}
    for co, r in rows:
        co = {k: v % p for k, v in co.items() if v % p}; r %= p
        changed = True
        while co:
            k = min(co)
            if k in piv:
                pc, pr = piv[k]; m = co[k]
                for kk, vv in pc.items(): co[kk] = (co.get(kk, 0) - m * vv) % p
                co = {kk: vv for kk, vv in co.items() if vv}; r = (r - m * pr) % p
            else:
                inv = pow(co[k], p - 2, p); co = {kk: vv * inv % p for kk, vv in co.items()}; r = r * inv % p
                piv[k] = (co, r); break
        else:
            if r: return False
    return True
for j in range(1, 6):
    M = 5 ** j; rows = []
    for L in range(5 * M):
        LL = L + 5 * M * 1000 + 60 * 5 * M   # a large representative (g needs L >= 60), same residue mod 5^(j+1)
        a, b = g(LL) % M, LL % M
        co = {}
        co[a] = co.get(a, 0) + 1; co[b] = co.get(b, 0) - 1
        rows.append((co, A[LL % 5]))
    print('j=%d coboundary mod 5 exists: %s' % (j, solve(rows, M)))
print('with a step-count term (P + lam*t, t += 3 per step):')
for kap in range(5):
    for j in range(1, 5):
        M = 5 ** j; rows = []
        for L in range(5 * M):
            LL = L + 5 * M * 1000 + 60 * 5 * M
            co = {}; a, b = g(LL) % M, LL % M
            co[a] = co.get(a, 0) + 1; co[b] = co.get(b, 0) - 1
            rows.append((co, A[LL % 5] + kap))
        r = solve(rows, M)
        if r: print(' kappa=%d j=%d: coboundary EXISTS' % (kap, j))
print('done')
