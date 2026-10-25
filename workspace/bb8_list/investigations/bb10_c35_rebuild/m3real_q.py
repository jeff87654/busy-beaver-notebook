"""Quick real-class check at r = 5899 (correct mod 8, 3, 5, 7, 11): the end-game sequences only, printing each case.
first counter on F1: S2(11), S3(7), S4(3->0), S1(0), refill S2(0); second counter on F2: S3(C'), S4(8), S1(5), S2(5->1), halt S3(1)."""
from m3rules_lib import chk
r = 5899; x = 2 * r + 3
n = bad = 0
for N in (1, 2):
    F1 = [6] * N + [3]; F2 = [6] * N + [0, 2, 0]
    for Z in (1, 2, 3, 7, 12):
        cases = [
            ('S2(11)', F1 + [11, x, 0] + [1] * Z + [1, r, 2], F1 + [7, 2, 0, 2 * r + 4 - (x - 3) // 2] + [1] * (Z + x - 2) + [1, 1, 2]),
            ('S3(7)', F1 + [7, 2, 0, 2] + [1] * Z + [1, r, 2], F1 + [3, 2 * r + 6, 7] + [1] * (Z + 1) + [1, 1, 2]),
            ('S4(3)', F1 + [3, 2] + [1] * Z + [1, r, 2], F1 + [0, 2 * r + 6] + [1] * Z + [1, 2, 2]),
            ('refill', F1 + [0, x, 0] + [1] * Z + [1, r, 2], [6] * (N - 1) + [0, 2, 0, 2 * r - (x + 1) // 2, 2, 0, 5] + [1] * (Z + x + 7) + [1, 1, 2]),
            ('S3(C\')', F2 + [r - 2, 2, 0, 2] + [1] * Z + [1, r, 2], F2 + [r - 6, 2 * r + 6, 7] + [1] * (Z + 1) + [1, 1, 2]),
            ('S4(8)', F2 + [8, 2] + [1] * Z + [1, r, 2], F2 + [5, 2 * r + 6] + [1] * Z + [1, 2, 2]),
            ('S2(5)', F2 + [5, x, 0] + [1] * Z + [1, r, 2], F2 + [1, 2, 0, 2 * r + 4 - (x - 3) // 2] + [1] * (Z + x - 2) + [1, 1, 2]),
            ('halt', F2 + [1, 2, 0, 2] + [1] * Z + [1, r, 2], 'HALT'),
        ]
        if Z >= 2:
            cases.append(('S1(0)', F1 + [0, x, 3] + [1] * Z + [1, r, 2], F1 + [0, x, 0, 2 * r + 5] + [1] * (Z - 1) + [1, 1, 2]))
            cases.append(('S1(5)', F2 + [5, x, 3] + [1] * Z + [1, r, 2], F2 + [5, x, 0, 2 * r + 5] + [1] * (Z - 1) + [1, 1, 2]))
        for name, inp, exp in cases:
            n += 1
            ok = chk(name, inp, exp)
            bad += not ok
            print(N, Z, name, ok, flush=True)
print('total', n, 'mismatches', bad)
