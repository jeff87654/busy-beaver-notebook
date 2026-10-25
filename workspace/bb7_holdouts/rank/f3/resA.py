"""resA.py: residue evaluator for A1/A2 (and B1) rules mod 2^K. Values: acc a and refill digits are residues mod 2^K;
rebuild digits are exact small ints. D-counts are applied in closed form (f^d(a) = 3^d (a+5/2) - 5/2)."""
import idle  # noqa
import sys
K = 64
M = 1 << K


def fpow(d, a, mul=3, add=5):
    """f^d(a) mod 2^K for f(a) = 3a + add (add odd): f^d(a) = (3^d (2a+add) - add)/2; d, a residues mod 2^K."""
    M2 = 2 * M
    t = pow(3, d % M, M2)
    return (((t * (2 * a + add) - add) % M2) // 2) % M


def run_list(ds, a, f_add=5, refill_add=6, a_after=2, absorb_add=2):
    """process list ds (exact small digits, list of ints) with acc a (residue) by A1 rules until an exhaustion.
    returns (variant, a): variant 'E' ([;a]), 'E1' ([0;a]), 'E2' ([0,0;a])."""
    ds = list(ds)
    while True:
        if not ds: return 'E', a
        d = ds[-1]
        if d != 0:
            a = fpow(d, a, add=f_add); ds[-1] = 0
            continue
        if len(ds) == 1: return 'E1', a
        if ds[-2] == 0:
            if len(ds) == 2: return 'E2', a
            a = (a + ds[-3] + absorb_add) % M
            del ds[-3:]
            continue
        # B1 chain on y = ds[-2]: refill R=3a+6 (residue), a=2, then D^R
        y = ds[-2]
        for _ in range(y):
            R = (3 * a + refill_add) % M
            a = fpow(R, a_after, add=f_add)
        ds[-2] = 0
        # now [.., 0, 0]? no: ds[-2]=0 and ds[-1]=0 -> next loop absorbs or E2


if __name__ == '__main__':
    import random
    # unit test fpow
    for _ in range(200):
        d = random.randint(0, 300); a = random.randint(0, 10**6); x = a
        for _ in range(d): x = 3 * x + 5
        assert fpow(d, a) == x % M
    print('fpow ok')
    random.seed(1)
    for top, tail, a0 in (([3], [1], 2), ([3], [], 2), ([3], [1], 14)):
        for n in range(60, 75):
            res = set()
            for t in range(4):
                a = random.randrange(M) if t else a0
                res.add(run_list(top + [2] * n + tail, a))
            print(top, 'n', n, tail, a0, 'n%3', n % 3, [(v, x % 64) for v, x in res])
