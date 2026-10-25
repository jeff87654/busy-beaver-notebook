"""Champion clearing modulo M.  Numbers < M are exact, numbers in [M, 2M) are representatives of huge values (mod M).
C(k, r, d): level-k digit d (a-token level 1), lower digits 0, accumulator r (r = 2 mod 3) -> final accumulator."""
from functools import lru_cache
M = 504
CNT = 168          # iteration counts derived from representatives are known mod CNT
import os
OFF = int(os.environ.get('REPOFF', '1'))
def red(v): return v if v < M else OFF * M + v % M
def big(v): return v >= M
def pow2(d, mod):  # d exact or big-representative of a huge exponent
    return pow(2, d, mod) if not big(d) else pow(2, CNT + d % CNT, mod)   # huge exponent: >= 3 and same residue mod 168 (lambda(504)=6 | 168)
@lru_cache(maxsize=None)
def C(k, r, d):
    if k == 1:
        if not big(d) and not big(r):
            return red(2**d * (r + 4) - 4) if d < 64 else red((pow(2, d, M) * (r + 4) - 4) % M + M)
        return red((pow2(d, M) * (r + 4) - 4) % M + M)
    g = lambda x: C(k - 1, 2, red((2 * x + 2) // 3) if not big(x) else digit_of_big(x))
    return iterate(g, r, d)
def digit_of_big(x):
    # x = huge accumulator (rep in [M,2M)), x = 2 mod 3; digit (2x+2)/3 is huge and known mod 2M/3 = 336 (we keep it mod CNT)
    assert x % 3 == 2, x
    v = ((2 * x + 2) // 3) % CNT
    return OFF * M + v            # big rep; only its residue mod CNT is meaningful
def iterate(g, x, d):
    if not big(d):
        for _ in range(d): x = g(x)
        return x
    seen = {}; seq = []
    while x not in seen:
        seen[x] = len(seq); seq.append(x); x = g(x)
    pre = seen[x]; cyc = len(seq) - pre
    assert CNT % cyc == 0, f'cycle length {cyc} does not divide {CNT}'
    pos = pre + ((d % CNT) - pre) % cyc if (d % CNT) >= pre else pre + ((d % CNT) - pre) % cyc
    return seq[pos]
if __name__ == '__main__':
    for k in range(1, 7):
        print(k, [C(k, 2, M + j) for j in range(6)])
