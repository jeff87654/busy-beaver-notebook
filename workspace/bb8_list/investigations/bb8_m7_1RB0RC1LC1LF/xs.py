import itertools
import planner8 as pl
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
pl.set_tm(M)
blocks=[(0,1,0),(1,0,0),(0,0,1),(1,0,0,0,1,0),(0,0,1,0,0,1)]
res=[]
for xs in blocks:
    for q in 'ABCDEFGH':
        for d in '><':
            for nb in range(0,4):
                for behind in itertools.product([0,1],repeat=nb):
                    lm,why=pl.derive_crossing(q,d,xs,list(behind))
                    if lm:
                        res.append((xs,q,d,behind,lm['ys'],lm['ctx']))
for r in res: print(r)
