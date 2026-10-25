import idle, subprocess, sys
from mprobe import run
from groups import G as G0
G = dict(G0)
G.update({
 '1LH/1LA': '1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LA',
 '1LH/1LD': '1RB0RG_1RC1RB_0RD1LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LD',
})
sel = sys.argv[1:] or list(G)
for name in sel:
    M = G[name]
    print('=====', name, M)
    for A in (21, 22, 23, 24):
        for j in (17, 18):
            for z in (30, 31):
                ev = run(M, A, j, [1], [0] * z, maxs=100000000, maxev=3)
                print('  A=%d j=%d z=%d:' % (A, j, z), ' | '.join(e[:120] for e in ev[:3]))
