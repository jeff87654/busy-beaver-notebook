import itertools
import planner8 as pl
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
pl.set_tm(M)
seen=set()
for L in (3,):
  for xs in itertools.product([0,1],repeat=L):
    for q in 'ABCDEFGH':
        for d in '><':
            for nb in range(0,5):
                for behind in itertools.product([0,1],repeat=nb):
                    lm,why=pl.derive_crossing(q,d,xs,list(behind))
                    if lm:
                        key=(xs,q,d,lm['ys'],lm['ctx'])
                        if key in seen: continue
                        seen.add(key)
                        print(''.join(map(str,xs)),q,d,'->',''.join(map(str,lm['ys'])),'ctx',lm['ctx'],'minbehind',behind)
