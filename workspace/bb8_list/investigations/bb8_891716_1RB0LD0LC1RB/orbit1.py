import sys,os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
from kfam import parse_at, set_shape
from tmlit import Sim, ST
TM="1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---"
set_shape('B','011')
s=Sim(TM,size=1<<20)
N=int(sys.argv[1]); ev=0
last=None
for n in range(N):
    if not s.step(): print('HALT',s.steps); break
    r=parse_at(s)
    if r:
        print(s.steps,r); ev+=1
        if ev>int(sys.argv[2]): break
