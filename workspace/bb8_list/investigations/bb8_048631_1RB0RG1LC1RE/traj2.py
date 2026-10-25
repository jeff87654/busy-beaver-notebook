import os, sys
os.environ['BB_KENC'] = '10,0'
from kfam import run_from, set_shape, show, trailing_zeros
from tmlit import Sim
set_shape('A', '111')
TM = '1LB0LG_1RC1LE_1RD0RD_0LA1RC_0LF0RC_1RG1LH_1RB1LG_1LF---'
N = int(sys.argv[1]);
s = Sim(TM, size=1 << 22)
last=0; n=0; stats={}
while s.steps < N:
    r = run_from(s, N - s.steps)
    if r[0] != 'K':
        print('ended', r[:3]); break
    ds,a,b = r[2]
    n+=1
    if a==0:
        k=trailing_zeros(ds)
        kind = 'R4' if k==len(ds) else ('R2' if k==0 else ('R3<' if k<b else ('R3=' if k==b else 'R3>')))
        stats[kind]=stats.get(kind,0)+1
        if kind in('R3=','R3>','R4') : print('step %d %s %s b=%d k=%d len=%d'%(r[1],kind,show(r[2])[:80],b,k,len(ds)))
print(stats, s.steps)
