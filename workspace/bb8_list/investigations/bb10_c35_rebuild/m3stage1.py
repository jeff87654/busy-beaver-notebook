"""Stage 1 of M3: [D6^(4b+2), D2, D2, D0, D2, 0^(8b+49) | 0 | R] -> [D6^(4b+1), D3, D(2R+5), D8, 0^(8b+51) | 0 | b-token D2]."""
from m3rules_lib import chk
n = bad = 0
for b in list(range(1, 13)) + [30, 61]:
    for R in (19, 31, 43, 55, 91):
        inp = [6] * (4 * b + 2) + [2, 2, 0, 2] + [1] * (8 * b + 49) + [1, R, 2]
        exp = [6] * (4 * b + 1) + [3, 2 * R + 5, 8] + [1] * (8 * b + 51) + [1, 2, 2]
        n += 1
        ok = chk('st1', inp, exp)
        bad += not ok
        if not ok:
            from m3probe import nextj
            print('MISMATCH b', b, 'R', R, nextj(inp)[:150])
print('cases', n, 'mismatches', bad)
