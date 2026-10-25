import os, sys
os.environ['BB_KENC'] = '10,0'
from kfam import run_from, set_shape, show
from tmlit import Sim
import rules
set_shape('A', '111')
TM = '1LB0LG_1RC1LE_1RD0RD_0LA1RC_0LF0RC_1RG1LH_1RB1LG_1LF---'
N = int(sys.argv[1]); s = Sim(TM, size=1 << 22)
prev=None; n=0; mism=0; kinds={}
while s.steps < N:
    r = run_from(s, N - s.steps)
    if r[0] != 'K': print('ended', r[:3]); break
    cfg=r[2]
    if prev is not None:
        kd,p=rules.step(*prev); n+=1; kinds[kd]=kinds.get(kd,0)+1
        if p!=cfg: mism+=1; print('MISMATCH',r[1],show(prev),show(cfg),kd,p)
    prev=cfg
print('checked',n,'mism',mism,kinds, 'steps',s.steps, show(prev)[:100])
