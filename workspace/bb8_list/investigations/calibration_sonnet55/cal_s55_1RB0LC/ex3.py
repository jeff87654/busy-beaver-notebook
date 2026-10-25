import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show, is_run, norm_side
from ex1 import m_TRF
ONE3=(1,)*3
Lv=[V('l')]
def C(k,v='j'): return {v:k}
R4=[0,1,1,1,1,BLANK]
PH={}
def y3(cnt,const): return [0]+mkrun(ONE3,cnt,const)   # 0 1^(3*cnt+3*const)
PH['POP']=(('A',[1,0]+Lv,[0]+mkrun(ONE3,C(1,'u'))+[1],'>'),
           ('A',Lv,[0]+mkrun(ONE3,C(1,'u'),2)+[1],'>'))
PH['L1']=(('A',[BLANK],[0]+mkrun(ONE3,C(2))+[1,BLANK],'>'),
          ('A',mkrun((1,0),C(3),1)+[1,1,BLANK],R4,'>'))
PH['L3']=(('A',[1,1,BLANK],[0]+mkrun(ONE3,C(2),2)+[1,BLANK],'>'),
          ('A',[1,0,1,1,1,0]+mkrun((1,0),C(3),3)+[1,1,BLANK],R4,'>'))
PH['R0']=(('A',[1,1,1,0,1,0]+Lv,[0]+mkrun(ONE3,C(2),2)+[1,BLANK],'>'),
          ('A',mkrun((1,0),C(3),4)+[1,1,1,0]+Lv,R4,'>'))
PH['R0e']=(('A',[1,1,1,0,1,1,BLANK],[0]+mkrun(ONE3,C(2),2)+[1,BLANK],'>'),
          ('A',mkrun((1,0),C(3),4)+[1,1,1,1,BLANK],R4,'>'))
PH['Fin']=(('A',[1,1,1,1,BLANK],[0]+mkrun(ONE3,C(2),2)+[1,BLANK],'>'),
          ('A',[BLANK],[0]+[1]*9+mkrun(ONE3,C(2),2)+[1,BLANK],'>'))
if __name__=="__main__":
    for w in sys.argv[1:]:
        s,t=PH[w]
        sc,cfg=drive(w,s,t,matchers=[m_TRF],maxev=200,verbose=True)
