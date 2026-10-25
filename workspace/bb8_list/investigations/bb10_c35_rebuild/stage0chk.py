"""Stage 0 of candidate 1 from the record's exhaustion X(b, 35), b = 1 (mod 5): the first K-moment must be
[D9^((12b+8)/5), D11, D1^((24b+196)/5) | a = D1 | r = D2] (tokens farthest first).  Also fits the step count."""
import mf35, sys
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA_------'
bad = 0; pts = []
for b in range(1, int(sys.argv[1]) if len(sys.argv) > 1 else 102, 5):
    w, h, s = mf35.xword(b, 35)
    sv = mf35._server()
    sv.stdin.write(f'{M} {s} {h} 2000000000 4000000 600\n{w}\n'); sv.stdin.flush()
    o = sv.stdout.readline().strip().rpartition(' | U=')[0]
    t = [int(x) for x in o.split('|')[1].split()][::-1]
    far = o.split('|')[2].strip()
    exp = [9] * ((12 * b + 8) // 5) + [11] + [1] * ((24 * b + 196) // 5) + [1, 2, 2]
    ok = t == exp and far == ''
    bad += not ok
    pts.append((b, int(o.split()[1])))
    print(b, 'OK' if ok else 'MISMATCH ' + mf35.rle(t), o.split()[1], flush=True)
# quadratic fit of the step count on the first three points, checked on all
(b0, s0), (b1, s1), (b2, s2) = pts[:3]
from fractions import Fraction as F
A = F((s2 - s1) * (b1 - b0) - (s1 - s0) * (b2 - b1), (b2 - b1) * (b1 - b0) * (b2 - b0))
B = F(s1 - s0, b1 - b0) - A * (b1 + b0)
C = s0 - A * b0 * b0 - B * b0
print('steps =', A, 'b^2 +', B, 'b +', C, ' fits all:', all(A * b * b + B * b + C == s for b, s in pts))
print('mismatches', bad)
