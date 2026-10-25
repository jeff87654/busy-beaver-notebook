import sys,os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
from kfam import run_next, set_shape
TM=os.environ.get('TM',"1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
set_shape('B','011')
def show(v):
    if v[0]=='K': return 'K(%s; %d; %d)'%(','.join(map(str,v[2][0])),v[2][1],v[2][2])
    return str(v[:3])
mode=sys.argv[1]
if mode=='r3':
    for b in range(0,9):
      for k in range(0,2*b+5):
        for y1 in (1,2):
            v=run_next(TM,(y1,)+(0,)*k,0,2*b+1,N=3*10**6)
            print('b=%d k=%d y+1=%d ->'%(b,k,y1),show(v), v[1] if v[0]=='K' else '')
elif mode=='r4':
    for b in range(0,9):
      for n in range(0,8):
            v=run_next(TM,(0,)*n,0,2*b+1,N=3*10**6)
            print('b=%d n=%d ->'%(b,n),show(v), v[1] if v[0]=='K' else '')
