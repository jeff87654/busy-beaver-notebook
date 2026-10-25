import itertools
import planner8 as P
TM = "1RB0RF_1RC0LF_0RD0RB_1LE1LG_0LA0LC_0LD1RH_1RA1LC_1RF---"
P.set_tm(TM)
blocks = []
for L in range(1, 5):
    for b in itertools.product((0, 1), repeat=L):
        blocks.append(b)
for q in 'ABCDEFGH':
    for d in '<>':
        for b in blocks:
            for behind in ([0]*6, [1]*6, [1,0]*3, [0,1]*3):
                lm, why = P.derive_crossing(q, d, b, behind)
                if lm:
                    print(q, d, ''.join(map(str, b)), '->', ''.join(map(str, lm['ys'])), 'ctx', lm['ctx'], 'behind', behind[:3])
