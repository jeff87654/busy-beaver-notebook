"""Exact literal check of the BB(10) champion's R4 on the used-up list Kd [] 0 b, b = 0..BMAX:
b odd -> halt (E0) with b+3 ones (b+4 after the final 1RZ write); b = 4m -> Kd [1,(0,0,3)^m,0,0,2] 0 0;
b = 4m+2 -> Kd [3,(0,0,3)^m,0,0,2] 0 0.  Also fits the step counts."""
import sys
from rules import *
M = sys.argv[1] if len(sys.argv) > 1 and '_' in sys.argv[1] else CH10
BMAX = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 200
bad = 0
steps = {}
for b in range(BMAX + 1):
    p = r4_ch10(b)
    r = run_next(M, (), 0, b, N=10 ** 8)
    if p[0] == 'HALT':
        ok = r[0] == 'HALT' and r[2] == ('E', 0) and r[3].ones() == b + 3
    else:
        ok = r[0] == 'K' and r[2] == p[1]
    steps[b] = r[1]
    if not ok:
        bad += 1
        print('MISMATCH b=%d pred %s got %s' % (b, p, r[:3]))
print('R4 check b=0..%d: %d mismatches' % (BMAX, bad))
# step-count fits per residue class mod 4: quadratic in m
for res in range(4):
    bs = [b for b in steps if b % 4 == res]
    m = [(b - res) // 4 for b in bs]
    import fractions
    F = fractions.Fraction
    # fit s = c2 m^2 + c1 m + c0 from first three points, then check all
    (m0, s0), (m1, s1), (m2, s2) = [(m[i], steps[bs[i]]) for i in range(3)]
    c2 = F(s2 - 2 * s1 + s0, 2)
    c1 = F(s1 - s0) - c2 * (2 * m0 + 1)
    c0 = F(s0) - c2 * m0 * m0 - c1 * m0
    okfit = all(c2 * mm * mm + c1 * mm + c0 == steps[b] for mm, b in zip(m, bs))
    print('b = 4m+%d: steps = %s m^2 + %s m + %s  (fits all: %s)' % (res, c2, c1, c0, okfit))
