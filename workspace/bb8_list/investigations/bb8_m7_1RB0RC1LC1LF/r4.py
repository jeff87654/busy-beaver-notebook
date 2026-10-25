import sys
sys.path.insert(0,'../rebuilder_nbrs')
from usage_phases import Tmpl, parse_tm, ST, run
from r4grid import mirror, tmpl_from
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
TS='L,G,P=1001,u=010,s=001,d=1d+0,b=1b+0,S=-'
o,T=tmpl_from(TS)
tm=parse_tm(mirror(M))
for n in range(0,5):
    for b in range(0,14):
        out,st,use,k=run(tm,T,T.build((0,)*n,0,b),stop_any=True,cap=2000000)
        print(n,b,out,st,k)
