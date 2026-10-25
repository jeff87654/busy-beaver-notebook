"""Boot search 1: keep Wade's 5-state boot, vary only the exit transition (D,1) -> (w,d,target)
over framework states the zf2 program needs anyway (6.continue.4 removed)."""
import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
import lowprio_local
from common import *
from tmfast import *
z = zf2.ZF2(); z.AXIOMORDER = AXIOMORDER; z.build_machine()
start, tbl = from_tm(z.tm)
del tbl[('6.continue.4','0')]; del tbl[('6.continue.4','1')]
targets = sorted({s for s,_ in tbl if s[0] in '123456'})
res=[]
for tg in targets:
    for w in '01':
        for d in 'LR':
            t=dict(tbl); t[('0.boot.D','1')]=(w,d,tg)
            r=run_until(t,start,'main().0',300000)
            if r is None: continue
            tape,pos,steps=r
            ok,g,nr,why=boot_check(tape,pos)
            res.append((ok,g,nr,steps,w,d,tg,why))
for x in sorted(res, key=lambda x:(not x[0],-x[1])):
    print(x)
