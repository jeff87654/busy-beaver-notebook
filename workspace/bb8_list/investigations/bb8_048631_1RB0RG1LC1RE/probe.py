import os, sys
os.environ['BB_KENC'] = '10,0'
from kfam import run_next, set_shape, show
set_shape('A', '111')
TM = '1LB0LG_1RC1LE_1RD0RD_0LA1RC_0LF0RC_1RG1LH_1RB1LG_1LF---'
for b in range(1,5):
  for y1 in (1,2,3):
    for k in range(1,b+5):
        ds=(1,y1)+(0,)*k
        r=run_next(TM,ds,0,b,N=10**6)
        print('b=%d k=%d'%(b,k), show((ds,0,b)), '->', show(r[2]) if r[0]=='K' else r[:3], r[1])
