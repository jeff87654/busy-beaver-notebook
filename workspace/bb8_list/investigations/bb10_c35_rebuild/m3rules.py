"""Literal grid check of the period map of M3 = 1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LJ_0LD0RA.
Tokens far-first; [.. | a | r] with a = D1 (a = 0); every check runs the literal machine (stage35.exe) from the input
K-moment to its next jump K-moment (or halt).  Far parts: F1 = D6^N D3 (first counter), F2 = D6^N D0 D2 D0 (second).
  S1: F [C, x, 3] 0^Z | R          -> F [C, x, 0, 2R+5] 0^(Z-1) | 0 | 1
  S2: F [C, x, 0] 0^Z | R          -> F [C-4, 2, 0, 2R+4-(x-3)/2] 0^(Z+x-2) | 0 | 1
  S3: F [C, 2, 0, 2] 0^Z | R       -> F [C-4, 2R+6, 7] 0^(Z+1) | 0 | 1
  S4: F [C, 2] 0^Z | R             -> F [C-3, 2R+6] 0^Z | 0 | b-token 2
  refill (F1, C = 0): D6^N D3 [0, x, 0] 0^Z | R -> D6^(N-1) D0 D2 D0 [2R-(x+1)/2, 2, 0, 5] 0^(Z+x+7) | 0 | 1
  halt (F2, C = 1):   F2 [1, 2, 0, 2] 0^Z | R    -> halts reading I0"""
import sys
from m3probe import nextj
def chk(name, toks, exp):
    got = nextj(toks, raw=True)
    if exp == 'HALT':
        ok = isinstance(got, str) and got.startswith('H') and got.split()[2] == 'I' and got.split()[3] == '0'
    else:
        ok = not isinstance(got, str) and got[0] == exp and got[1] == ''
    return ok
if __name__ != "__main__":
    raise ImportError("skip")
n = bad = 0
Ns = (1, 2, 4)
Cs = (4, 5, 7, 8, 11, 12, 16, 23, 30)
xs = (17, 29, 41, 53, 65)
Rs = (19, 31, 43, 55, 67, 91)
Zs = (3, 8, 20, 45)
fails = []
for N in Ns:
    for F in ([6] * N + [3], [6] * N + [0, 2, 0]):
        for R in Rs:
            for Z in Zs:
                for C in Cs:
                    cases = []
                    for x in xs:
                        cases.append(('S1', F + [C, x, 3] + [1] * Z + [1, R, 2], F + [C, x, 0, 2 * R + 5] + [1] * (Z - 1) + [1, 1, 2]))
                        if 2 * R + 4 - (x - 3) // 2 >= 5:
                            cases.append(('S2', F + [C, x, 0] + [1] * Z + [1, R, 2],
                                          F + [C - 4, 2, 0, 2 * R + 4 - (x - 3) // 2] + [1] * (Z + x - 2) + [1, 1, 2]))
                    cases.append(('S3', F + [C, 2, 0, 2] + [1] * Z + [1, R, 2], F + [C - 4, 2 * R + 6, 7] + [1] * (Z + 1) + [1, 1, 2]))
                    if C >= 3:
                        cases.append(('S4', F + [C, 2] + [1] * Z + [1, R, 2], F + [C - 3, 2 * R + 6] + [1] * Z + [1, 2, 2]))
                    for name, inp, exp in cases:
                        n += 1
                        if not chk(name, inp, exp):
                            bad += 1; fails.append((name, N, len(F), C, R, Z))
            for Z in Zs:
                if len(F) == N + 1:
                    for x in xs:
                        if 2 * R - (x + 1) // 2 >= 5:
                            n += 1
                            exp = [6] * (N - 1) + [0, 2, 0, 2 * R - (x + 1) // 2, 2, 0, 5] + [1] * (Z + x + 7) + [1, 1, 2]
                            if not chk('refill', F + [0, x, 0] + [1] * Z + [1, R, 2], exp):
                                bad += 1; fails.append(('refill', N, x, R, Z))
                else:
                    n += 1
                    if not chk('halt', F + [1, 2, 0, 2] + [1] * Z + [1, R, 2], 'HALT'):
                        bad += 1; fails.append(('halt', N, R, Z))
    print('N', N, 'cases so far', n, 'mismatches', bad, flush=True)
print('total cases', n, 'mismatches', bad)
for f in fails[:40]:
    print('FAIL', f)
