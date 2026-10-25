import sys,os
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
import kfam
from kfam import kstart, parse_at, set_shape
TM=os.environ.get('TM',"1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
set_shape('B','011')
def trace(ds,a,b,N=3000,maxev=12):
    s=kstart(TM,ds,a,b)
    ev=0
    print('start',ds,a,b)
    for n in range(N):
        if not s.step():
            print('HALT at',s.steps); return
        r=parse_at(s)
        if r: 
            print(s.steps,r); ev+=1
            if ev>=maxev: return
if __name__=='__main__':
    ds=tuple(int(x) for x in sys.argv[1].split(',')) if sys.argv[1] else ()
    trace(ds,int(sys.argv[2]),int(sys.argv[3]),N=int(sys.argv[4]) if len(sys.argv)>4 else 3000)
