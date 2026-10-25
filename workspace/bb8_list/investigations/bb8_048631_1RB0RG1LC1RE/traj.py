import os, sys
os.environ['BB_KENC'] = '10,0'
from kfam import run_from, set_shape, show
from tmlit import Sim
set_shape('A', '111')
TM = '1LB0LG_1RC1LE_1RD0RD_0LA1RC_0LF0RC_1RG1LH_1RB1LG_1LF---'
N = int(sys.argv[1]); 
s = Sim(TM, size=1 << 22)
last=0; n=0
while s.steps < N:
    r = run_from(s, N - s.steps)
    if r[0] != 'K':
        print('ended', r[:3]); break
    n+=1
    if n<60 or n%500==0: print('step %d: %s (+%d)' % (r[1], show(r[2]), r[1]-last))
    last=r[1]
