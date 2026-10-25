import sys
sys.path.insert(0,'../rebuilder_nbrs')
from usage_phases import Tmpl, parse_tm, ST
from r4grid import mirror, tmpl_from
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
TS='L,G,P=1001,u=010,s=001,d=1d+0,b=1b+0,S=-'
o,T=tmpl_from(TS)
tm=parse_tm(mirror(M))
tape={};pos=0;q=0
cnt=0
maxsteps=int(sys.argv[1]) if len(sys.argv)>1 else 200000
for step in range(1,maxsteps+1):
    s=tape.get(pos,0)
    tr=tm[(q,s)]
    if tr is None:
        print('HALT at step',step);break
    w,d,q=tr
    if w: tape[pos]=1
    else: tape.pop(pos,None)
    pos+=d
    if q==T.q and tape and pos>max(tape) and pos<=max(tape)+4:
        l=min(tape)
        x=''.join('1' if tape.get(i,0) else '0' for i in range(l,pos))
        k=T.parse(x)
        if k is not None:
            cnt+=1
            ds,a,b=k
            print(step,'K(',ds,';',a,';',b,')',flush=True)
