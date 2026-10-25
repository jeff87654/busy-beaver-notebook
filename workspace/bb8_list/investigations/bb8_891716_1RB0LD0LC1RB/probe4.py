import sys,os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
from kfam import run_next, set_shape
TM=os.environ.get('TM',"1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
set_shape('B','011')
def show(v):
    if v[0]=='K': return 'K(%s; %d; %d) steps %d'%(','.join(map(str,v[2][0])),v[2][1],v[2][2],v[1])
    return str(v[:3])
for b in (5,7,9,11):
  for k in range(1,9):
    print(b,k,show(run_next(TM,(1,3)+(0,)*k,0,b,N=10**7)))
