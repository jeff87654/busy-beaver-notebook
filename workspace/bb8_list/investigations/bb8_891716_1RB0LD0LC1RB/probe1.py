import sys,os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
import kfam
from kfam import run_next, set_shape
TM=sys.argv[1] if len(sys.argv)>1 else "1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---"
set_shape('B','011')
def show(v):
    if v[0]=='K': return 'K(%s; %d; %d) steps %d'%(','.join(map(str,v[2][0])),v[2][1],v[2][2],v[1])
    return str(v[:3])
print('R1')
for b in (1,3,5,7):
    print(b, show(run_next(TM,(2,),2,b,N=10**6)))
print('R2')
for b in (1,3,5,7):
    print(b, show(run_next(TM,(2,),0,b,N=10**6)))
print('R3')
for b in (1,3,5):
    for k in range(1,9):
        print(b,k, show(run_next(TM,(1,2)+(0,)*k,0,b,N=10**6)))
print('R4')
for b in range(1,10,2):
    print(b, show(run_next(TM,(),0,b,N=10**6)))
