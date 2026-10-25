"""stable tower residues.  Tw(m) = 2^^k mod m for all large k:  Tw(1)=0, Tw(m) = 2^(Tw(phi(m)) + phi(m)) mod m.
Deep clearing output in Ligocki units a = 2^^(...)-3  ->  a = Tw(m)-3 (mod m);  raw accumulator A = 3a+1.
Record: 2B+4 = 2^^37 3  ->  B = (Tw(2m)-4)/2 (mod m)."""
from functools import lru_cache


def factor(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def totient(n):
    r = n
    for p in factor(n):
        r = r // p * (p - 1)
    return r


@lru_cache(None)
def Tw(m):
    if m == 1:
        return 0
    p = int(totient(m))
    return pow(2, Tw(p) + p, m)


def check_tw(m, K=6):
    """brute force: 2^^k mod m for k up to K (exact towers via the same recursion with explicit small towers)"""
    t = 1
    vals = []
    for k in range(1, K + 1):
        t = 2 ** t if t < 64 else None
        if t is None:
            break
        vals.append(t % m)
    return vals


def a_deep(m):
    return (Tw(m) - 3) % m


def A_deep(m):
    return (3 * a_deep(m) + 1) % m


def B_rec(m):
    t = Tw(2 * m)
    assert (t - 4) % 2 == 0
    return ((t - 4) // 2) % m


if __name__ == '__main__':
    for m in [2, 3, 4, 5, 8, 9, 11, 16, 25, 121, 7]:
        print('m=%d Tw=%d a_deep=%d A_deep=%d B=%d' % (m, Tw(m), a_deep(m), A_deep(m), B_rec(m)))
    M = 18101949465600
    print('B mod 18101949465600 =', B_rec(M), ' (bb8-ab: 16537583495166)')
    Q = 54305848396800
    print('a_deep mod Q =', a_deep(Q), ' A_deep mod Q =', A_deep(Q), ' Tw(Q)=', Tw(Q))
    # sanity: small towers 2^^4=65536, 2^^5 = 2^65536
    # brute check: 2^^5 = 2^65536, 2^^6 = 2^(2^65536): compare with Tw for small m
    for m in [7, 11, 25, 40, 121, 1000]:
        t5 = pow(2, 65536, m)
        # 2^^6 mod m via exponent reduction with exact 2^65536 mod (huge multiple of the order)
        L = 1
        for k in range(1, 200):
            if pow(2, k + 64, m) == pow(2, 64, m):
                L = k; break
        t6 = pow(2, 64 + (pow(2, 65536, L * 10 ** 6) - 64) % L, m)
        print('m=%d 2^^5=%d 2^^6=%d Tw=%d' % (m, t5, t6, Tw(m)))
