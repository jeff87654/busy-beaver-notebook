"""Literal checks (stage35.exe, rcap 0 so every K-moment is reported) of the steps of candidate 1's jumps that lie
outside the Coq-proved R1-R3 (which assume tokens 3d+1):
  (i)  R3 with the non-standard accumulator token D2:  [.., X, 0^Z | a=0 | r=2]  -> [.., X-3, 9, 0^(Z-1) | 0 | 1]
  (ii) R3 from residue-0 tokens 9, 6, 3:               [.., m, 0^Z | 0 | r]      -> [.., m-3, 2r+5, 0^(Z-1) | 0 | 1]
       and R2 from them (Z = 0):                       [.., m | 0 | r]           -> [.., m-3 | 2r+5 | 1]
Prints the number of cases and mismatches."""
import mf35
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA_------'
def nextk(toks):
    w = mf35.word_of_tokens(toks)
    sv = mf35._server()
    sv.stdin.write(f'{M} G {len(w)} 50000000 400000 0\n{w}\n'); sv.stdin.flush()
    o = sv.stdout.readline().strip()
    o = o.rpartition(' | U=')[0] or o
    if not o.startswith('J'):
        return None
    t = [int(x) for x in o.split('|')[1].split()]
    return t[::-1]          # farthest first, incl. a, r, tail
bad = n = 0
for N in (1, 2, 3):
    for Z in list(range(1, 60)) + [100, 157, 300]:
        far = [9] * N
        # (i)
        got = nextk(far + [11] + [1] * Z + [1, 2, 2]); exp = far + [8, 9] + [1] * (Z - 1) + [1, 1, 2]
        n += 1; bad += got != exp
        if got != exp: print('i', N, Z, got and mf35.rle(got))
        for m in (9, 6, 3):
            for r in (1, 7, 19, 43):
                got = nextk(far + [8, m] + [1] * Z + [1, r, 2]); exp = far + [8, m - 3, 2 * r + 5] + [1] * (Z - 1) + [1, 1, 2]
                n += 1; bad += got != exp
                if got != exp: print('ii', N, Z, m, r, got and mf35.rle(got))
for m in (9, 6, 3):
    for r in (1, 7, 19, 43):
        got = nextk([9, 8, m, 1, r, 2]); exp = [9, 8, m - 3, 2 * r + 5, 1, 2]
        n += 1; bad += got != exp
        if got != exp: print('R2', m, r, got and mf35.rle(got))
print('cases', n, 'mismatches', bad)
