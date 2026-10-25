"""Extra literal checks for M3's period map at the counter boundaries and the first period (x = 5):
S4 with C = 3 (-> 0), S1 with C = 0, S2 with x = 5, all on the first-counter far part D6^N D3."""
from m3rules_lib import chk
n = bad = 0
for N in (1, 2, 4):
    F = [6] * N + [3]
    for R in (19, 31, 43, 55, 67, 91):
        for Z in (3, 8, 20, 45):
            for C in (3, 14, 25):
                n += 1; bad += not chk('S4', F + [C, 2] + [1] * Z + [1, R, 2], F + [C - 3, 2 * R + 6] + [1] * Z + [1, 2, 2])
            for x in (17, 41, 65):
                n += 1; bad += not chk('S1', F + [0, x, 3] + [1] * Z + [1, R, 2], F + [0, x, 0, 2 * R + 5] + [1] * (Z - 1) + [1, 1, 2])
            for C in (4, 15, 26, 40):
                n += 1; bad += not chk('S2x5', F + [C, 5, 0] + [1] * Z + [1, R, 2], F + [C - 4, 2, 0, 2 * R + 3] + [1] * (Z + 3) + [1, 1, 2])
print('cases', n, 'mismatches', bad)
