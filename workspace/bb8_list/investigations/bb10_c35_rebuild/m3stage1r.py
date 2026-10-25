"""Stage 1 of M3 in the real class: R in {355, 619, 5899} (r-token classes of the tower residues), b in {6, 11, 21, 126}."""
from m3rules_lib import chk
n = bad = 0
for b in (6, 11, 21, 126):
    for R in (355, 619, 5899):
        inp = [6] * (4 * b + 2) + [2, 2, 0, 2] + [1] * (8 * b + 49) + [1, R, 2]
        exp = [6] * (4 * b + 1) + [3, 2 * R + 5, 8] + [1] * (8 * b + 51) + [1, 2, 2]
        n += 1
        ok = chk('st1', inp, exp)
        bad += not ok
        print(b, R, ok, flush=True)
print('cases', n, 'mismatches', bad)
