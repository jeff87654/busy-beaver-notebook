"""M3 end-game and stage map in the REAL residue class (residues.py): every accumulator r = 3s+1 with s the tower
residue, r = 15139 (mod 27720).  Representatives r in {91, 355, 619, 5899}: correct mod {8,3,11}, {8,3,7,11},
{8,3,5,11}, {8,3,5,7,11} (all also r = 3 mod 4); x = 2r'+3 with r' in the same class.  Exact expected outputs (m3rules).
Checks, for N (D6 count) in 1..3 and Z = 1..12, 25, 40:
  first counter (far F1 = D6^N D3):  S2(C=11), S3(7), S4(3 -> 0), S1(0), S2(0) = refill, and generic S1-S4 at C = 30;
  second counter (far F2 = D6^N D0 D2 D0): S3(C'), S4, S1, S2(5 -> 1), S3(1) = halt at I0."""
from m3rules_lib import chk
n = bad = 0
fails = []
def T(name, inp, exp):
    global n, bad
    n += 1
    if not chk(name, inp, exp):
        bad += 1; fails.append(name)
for r in (91, 355, 619, 5899):
    x = 2 * r + 3
    for N in (1, 2, 3):
        F1 = [6] * N + [3]
        F2 = [6] * N + [0, 2, 0]
        for Z in list(range(1, 13)) + [25, 40]:
            for F, Cs in ((F1, (11, 30)), (F2, (5, 30))):
                for C in Cs:
                    T(f'S2 C={C}', F + [C, x, 0] + [1] * Z + [1, r, 2], F + [C - 4, 2, 0, 2 * r + 4 - (x - 3) // 2] + [1] * (Z + x - 2) + [1, 1, 2])
            for F, Cs in ((F1, (7, 30)), (F2, (2 * r - r - 2, 30))):
                for C in Cs:
                    T(f'S3 C={C}', F + [C, 2, 0, 2] + [1] * Z + [1, r, 2], F + [C - 4, 2 * r + 6, 7] + [1] * (Z + 1) + [1, 1, 2])
            for F, Cs in ((F1, (3, 30)), (F2, (8, 30))):
                for C in Cs:
                    T(f'S4 C={C}', F + [C, 2] + [1] * Z + [1, r, 2], F + [C - 3, 2 * r + 6] + [1] * Z + [1, 2, 2])
            for F, Cs in ((F1, (0, 30)), (F2, (5, 30))):
                for C in Cs:
                    if Z >= 2:
                        T(f'S1 C={C}', F + [C, x, 3] + [1] * Z + [1, r, 2], F + [C, x, 0, 2 * r + 5] + [1] * (Z - 1) + [1, 1, 2])
            T('refill', F1 + [0, x, 0] + [1] * Z + [1, r, 2], [6] * (N - 1) + [0, 2, 0, 2 * r - (x + 1) // 2, 2, 0, 5] + [1] * (Z + x + 7) + [1, 1, 2])
            T('halt', F2 + [1, 2, 0, 2] + [1] * Z + [1, r, 2], 'HALT')
    print('r', r, 'cases', n, 'mismatches', bad, sorted(set(fails))[:10], flush=True)
print('total', n, 'mismatches', bad)
