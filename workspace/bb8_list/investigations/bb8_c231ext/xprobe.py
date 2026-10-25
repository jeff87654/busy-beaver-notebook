import idle, subprocess, sys
from mprobe import run
from groups import G
_unused = {
 '0LH/1RC': '1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RC',
 '0LH/0LF': '1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LF',
 '0LH/0RC': '1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RC',
 '0LH/0RE': '1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RE',
 '1LH/0RA': '1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RA',
}
sel = sys.argv[1:] or list(G)
for name in sel:
    M = G[name]
    print('=====', name, M)
    for A in (7, 8, 9, 10):
        for j in (0, 1, 2, 3):
            for tail in ([0, 2, 2, 2, 2, 2, 2, 2, 2], [2] * 9):
                ev = run(M, A, j, [1], tail, maxs=50000000, maxev=4)
                print('  A=%d j=%d tail0=%d:' % (A, j, tail[0]), ' | '.join(e[:110] for e in ev[:4]))
