import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show, is_run, norm_side
ONE6=(1,)*6
Lv=[V('l')]
def m_TRF(cfg):
    q,L,R,mode=cfg
    if q=='F' and mode=='>' and L and L[0]==0 and R and is_run(R[0]) and all(x==1 for x in R[0][1]):
        run=R[0]; k=len(run[1])
        return ((q,norm_side([0,('run',run[1],run[2])]+L[1:]),R[1:],'>'),'follow TRF%d.'%k,'TRF%d'%k)
def show_run(): pass
MATCH=[m_TRF]
pop_s=('A',[1,0]+Lv,[0]+mkrun(ONE6,{'t':1})+[1,1,1,1,BLANK],'>')
pop_t=('A',Lv,[0]+mkrun(ONE6,{'t':1},1)+[1,1,1,1,BLANK],'>')
if __name__=="__main__":
    drive('pop',pop_s,pop_t,matchers=MATCH,maxev=100,verbose=True)
