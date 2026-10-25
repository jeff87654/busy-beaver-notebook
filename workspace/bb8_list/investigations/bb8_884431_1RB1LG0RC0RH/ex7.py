import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show, step, head, Stuck
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
pl.set_tm(ACT)
def cfgK(ds,a,bp):
    # actual: A> 0 0 1 1^bp 0 1^a 0 1^dn 0 ... 1^d1 0 0^inf
    R=[0,0,1]+[1]*bp+[0]+[1]*a+[0]
    for d in reversed(ds): R+= [1]*d+[0]
    R.append(BLANK)
    return ('A',[BLANK],pl.norm_side(R),'>')
if __name__=='__main__':
    ds=tuple(int(x) for x in sys.argv[1].split(',') if x); a=int(sys.argv[2]); bp=int(sys.argv[3])
    cfg=cfgK(ds,a,bp)
    n=0
    print(show(cfg))
    while n<int(sys.argv[4]):
        try: head(cfg)
        except Stuck: break
        try: cfg=step(cfg)
        except Exception as e: print(e); break
        n+=1
        if cfg[0] in sys.argv[5]  and cfg[3]=='>': print(n,show(cfg))
