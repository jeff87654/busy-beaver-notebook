"""End-game stages of M3: S2 with C = 0 (refill) and S3 with C = 1 (halt), over parameter grids."""
import mf35
from m3probe import nextj
F = [6] * 3
print('S2, C=0:')
for x in (17, 41, 65, 89):
    for R in (19, 25, 31, 43, 91, 103):
        for Z in (10, 37):
            toks = F + [3, 0, x, 0] + [1] * Z + [1, R, 2]
            print(f'  x={x} R={R} Z={Z} ->', nextj(toks), flush=True)
print('S3 / S2 with small C:')
for C in (0, 1, 2, 3):
    for R in (19, 25, 31, 43, 91):
        for Z in (10, 37):
            toks = F + [3, C, 2, 0, 2] + [1] * Z + [1, R, 2]
            print(f'  S3 C={C} R={R} Z={Z} ->', nextj(toks)[:90], flush=True)
