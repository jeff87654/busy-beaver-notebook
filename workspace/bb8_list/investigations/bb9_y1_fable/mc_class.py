"""mc_class.py : is C04/M8's endgame class (key, rho) pinned by the residues of the real orbit start?
The level-B cascade is one orbit of g(L) = (3L + c_{L mod 5})/5 (c = -100, 32, -46, -64, -52 for L mod 5 = 0..4) from
L1 = gstep(L0), L0 = 36B + 73 (Coq: Step.v L0/L1, reach_top: parked count P = 12 R2 + 11 at L1).  Each step consumes
cost(r) = 3 / 11 / 4 / 6 / 6 parked zeros for r = 0 / 1 / 2 / 3 / 4 (Coq CascU.casc_stepU: P - 3, P - 11, P - 4, P - 6, P - 6).
Key = first orbit value < 60.  For key 31 the five routes are indexed by rho = (P - 35) mod 5 (K31_End); d = 0 (Y1 halts
with sigma(M8) - 1) exactly for rho in {0, 4}.
Experiment: sample starts L0' that agree with the REAL L0 modulo M (M = a product of prime powers; residues of B from
towermod) and have the same shape (odd, = 1 mod 3, = 4 mod 5 ...), of a given size, and tabulate (key, rho).
If every (key, rho) occurs inside the real residue class mod M, no invariant "mod M" can decide the class.
usage: python mc_class.py N DIGITS [seed]
"""
import sys, random, collections
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_y1\tools')
from towermod import B_mod

C = {1: 32, 2: -46, 3: -64, 4: -52, 0: -100}
COST = {0: 3, 1: 11, 2: 4, 3: 6, 4: 6}

def gstep(L):
    return (3 * L + C[L % 5]) // 5

def run(L0):
    """orbit from L0: returns (key, sum of costs from L1 on, number of steps from L1, residue string of the last 12 steps)"""
    L = gstep(L0)                        # TOP1 (the special first step, r = 4); accounting starts at L1 with P = 12 R2 + 11
    assert L0 % 5 == 4
    cost = 0; n = 0; rs = []
    while L >= 60:
        r = L % 5; cost += COST[r]; rs.append(r); n += 1
        L = gstep(L)
    return L, cost, n, ''.join(map(str, rs[-12:]))

def main():
    N = int(sys.argv[1]); DIG = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    rnd = random.Random(seed)
    # modulus: 2^12 3^6 5^6 7 11 13 17 19 23 29 31
    M = 2 ** 12 * 3 ** 6 * 5 ** 6 * 7 * 11 * 13 * 17 * 19 * 23 * 29 * 31
    Bm = B_mod(M)
    L0m = (36 * Bm + 73) % M
    R2m5 = 1                              # R2 = 1 mod 5 (2 R2 + 4 = 2^^(12B+26) 4 = 1 mod 5)
    P1m5 = (12 * R2m5 + 11) % 5           # parked count at L1, mod 5
    print('M = %d   B mod M = %d   L0 mod M = %d  (L0 mod 5 = %d, mod 3 = %d, mod 2 = %d)' % (M, Bm, L0m, L0m % 5, L0m % 3, L0m % 2))
    # the real orbit's known prefix (determined by L0 mod 5^6 : 6 steps incl. TOP1)
    cnt = collections.Counter(); byrho = collections.Counter(); ex = {}
    lo = 10 ** (DIG - 1); hi = 10 ** DIG
    for i in range(N):
        k = rnd.randrange(lo // M, hi // M)
        L0 = L0m + M * k
        key, cost, n, tail = run(L0)
        rho = (P1m5 - cost - 35) % 5
        cls = (key, rho if key == 31 else -1)
        cnt[cls] += 1
        if cls not in ex: ex[cls] = (L0 % 10 ** 12, n, tail)
    print('samples %d, %d-digit starts, all = real L0 mod M' % (N, DIG))
    d0 = 0
    for cls in sorted(cnt):
        key, rho = cls
        d = {0: 0, 1: 1, 2: 'big', 3: 1, 4: 0}[rho] if key == 31 else {37: 7, 43: 9, 49: 3, 55: 'big'}[key]
        if d == 0: d0 += cnt[cls]
        print('key %2d rho %2s : %6d  (%.4f)   d=%s   e.g. L0 mod 1e12=%d steps=%d tail=%s' %
              (key, rho if rho >= 0 else '-', cnt[cls], cnt[cls] / N, d, *ex[cls]))
    print('d = 0 classes (Y1 halts with sigma(M8)-1): %d / %d = %.4f' % (d0, N, d0 / N))

if __name__ == '__main__':
    main()
