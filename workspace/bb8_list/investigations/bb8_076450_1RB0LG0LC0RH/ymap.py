"""Exact Y-map (small n) and 3-adic residue trajectory for large n.
Y(n) = 0^inf A> 0 1^n 0^inf.
f(3k)   = (20*4^k + 7)/3            (k >= 1)
f(3k+1) = 5 (k=0), 13 (k=1), HALT (k=2), (104*4^(k-3) + 7)/3 (k >= 3)
f(3k+2) = HALT
"""
import sys

def f_exact(n):
    k, r = divmod(n, 3)
    if r == 2: return None
    if r == 0:
        assert k >= 1
        return (20 * 4**k + 7) // 3
    if k == 0: return 5
    if k == 1: return 13
    if k == 2: return None
    return (104 * 4**(k - 3) + 7) // 3

def f_mod_exact_input(n, M):
    """n exact (possibly large, k>=3); return f(n) mod 3^M or None."""
    k, r = divmod(n, 3)
    mod = 3**(M + 1)
    if r == 2: return None
    if r == 0: v = (20 * pow(4, k, mod) + 7) % mod
    else: v = (104 * pow(4, k - 3, mod) + 7) % mod
    assert v % 3 == 0
    return v // 3

def f_mod(n_res, M):
    """n known mod 3^M (M>=2), n large (k>=3). Return f(n) mod 3^(M-1), or None for halt."""
    mod = 3**M
    r = n_res % 3
    if r == 2: return None
    k = (n_res - r) // 3 % 3**(M - 1)       # k mod 3^(M-1); ord(4 mod 3^M) = 3^(M-1)
    if r == 0:
        v = (20 * pow(4, k, mod) + 7) % mod
    else:
        v = (104 * pow(4, (k - 3) % 3**(M - 1), mod) + 7) % mod
    assert v % 3 == 0
    return (v // 3) % 3**(M - 1)

if __name__ == '__main__':
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    n = 4
    traj = [n]
    while n is not None and n < 10**6:
        n = f_exact(n); traj.append(n)
    if traj[-1] is None:
        print('exact trajectory:', traj); print('halts at small n'); sys.exit()
    print('exact trajectory: n_0..n_%d =' % (len(traj) - 1), traj[:-1], '; n_%d = (formula, %d digits)' % (len(traj) - 1, len(str(n))))
    i = len(traj) - 1
    m = M
    res = n % 3**m
    while m >= 2:
        r = res % 3
        print('n_%d mod 3 = %d  (known mod 3^%d; n_%d mod 3^%d = %d)' % (i, r, m, i, min(m, 6), res % 3**min(m, 6)))
        if r == 2:
            print('=> Y(n_%d) halts' % i); break
        res = f_mod(res, m); m -= 1; i += 1
