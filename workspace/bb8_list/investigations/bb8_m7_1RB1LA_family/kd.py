import os,sys
os.environ['BB_KENC']='10,00'
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\neighbors_family_tools')
import kfam
kfam.set_shape('D','10')
from kfam import run_from, run_next, show
from tmlit import Sim
TM='1RB1LA_1LC1LF_1RD0LB_1RA1LE_0RC0LC_0LD0RG_0RH0RF_---0LB'
def fmt(f):
    ds,a,bu=f
    return 'K(%s; %s; bu=%s)'%(','.join(map(str,ds)),a,bu)
if __name__=='__main__':
    N=int(sys.argv[1]) if len(sys.argv)>1 else 200000
    s=Sim(TM)
    last=0
    while s.steps<N:
        r=run_from(s,N-s.steps)
        if r[0]!='K':
            print(r[:3]);break
        print('step',r[1],fmt(r[2]),'[+%d]'%(r[1]-last)); last=r[1]
