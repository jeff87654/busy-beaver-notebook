import sys, idle_guard
from fam import *
from coding import ChampCoding
C = ChampCoding()
TF = [0, 3, 0, 1]
for name, m in [('champion', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF'), ('M8', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---')]:
    # sanity: symbolic plain decrement
    for n0 in (1, 3, 11):
        res = []
        for r in range(0, 12):
            tp = C.encode([0] * n0 + ['H%d' % r], TF, 0, 'B')
            v, st, fin, raw = run_sym(m, 'B', tp, stopn=3, mg=720, hlb=1000, budget=2000000, tlimit=60, prove=True)
            res.append((r, v, fin[:90] if fin and v != 'HALT' else ''))
        print(name, 'exhaustion [0^%d, X] classes r<12:' % n0, [(r, v) for r, v, f in res])
        for r, v, f in res[:2]: print('    ', r, v, f)
