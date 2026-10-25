"""The verifier's objection: in the real run the accumulator R entering S2 is far smaller than the unpacked token x
(x = 2 R3 + 3 from the previous period's S4 input R3, while R comes from a reset after the S4 jump).  Test S2,
F1 [C, x, 0] 0^Z | R, literally for R << x (x = 2r'+3, r' in the real class, r' >> R), and locate the boundary."""
import sys
from m3probe import nextj
import mf35
F1 = [6] * 3 + [3]
print('boundary scan, C = 30, Z = 10:')
for R in (19, 31, 43):
    row = []
    for rp in range(R, 4 * R + 40, 6):
        x = 2 * rp + 3
        o = nextj(F1 + [30, x, 0] + [1] * 10 + [1, R, 2], maxs=2_000_000_000, raw=True)
        y = 2 * R + 4 - (x - 3) // 2
        row.append(f"r'={rp}(y={y}):" + ('H' if isinstance(o, str) and o.startswith('H') else 'J' if not isinstance(o, str) else o[:1]))
    print(f'  R={R}:', ' '.join(row), flush=True)
print('real-class sizes (R << x):')
for R in (19, 91, 355):
    for rp in (619, 5899):
        if rp <= R:
            continue
        for Z in (3, 10, 25):
            for C in (30, 715 - 11):
                x = 2 * rp + 3
                o = nextj(F1 + [C, x, 0] + [1] * Z + [1, R, 2], maxs=4_000_000_000, raw=True)
                res = o[:60] if isinstance(o, str) else 'J ' + mf35.rle(o[0])[:90]
                print(f'  R={R} x={x} Z={Z} C={C}: {res}', flush=True)
