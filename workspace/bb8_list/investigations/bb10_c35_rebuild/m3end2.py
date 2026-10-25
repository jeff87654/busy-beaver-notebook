"""Second-counter stages of M3 (far part after the refill: D6^N D0 D2 D0): S3, S4, S1, S2 for general C, and the
end-game S3 with C = 1.  Compares against the first-counter stage forms."""
from m3probe import nextj
import mf35
for N in (2, 5):
    G = [6] * N + [0, 2, 0]
    for R in (19, 25, 43, 91):
        for Z in (10, 37):
            print(f'N={N} R={R} Z={Z}:')
            print('   S3 C=1  ->', nextj(G + [1, 2, 0, 2] + [1] * Z + [1, R, 2]))
            print('   S3 C=12 ->', nextj(G + [12, 2, 0, 2] + [1] * Z + [1, R, 2]))
            print('   S4 C=8  ->', nextj(G + [8, 2] + [1] * Z + [1, R, 2]))
            print('   S1 C=5  ->', nextj(G + [5, 2 * R + 3, 3] + [1] * Z + [1, R, 2]))
            print('   S2 C=5  ->', nextj(G + [5, 2 * R + 3, 0] + [1] * Z + [1, 2 * R + 1, 2]), flush=True)
