import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show, is_run, norm_side
from ex1 import m_TRF
ONE6=(1,)*6
Lv=[V('l')]
def J(k): return {'j':k}
R4=[0,1,1,1,1,BLANK]
PH={}
PH['L1']=(('A',[BLANK],[0]+mkrun(ONE6,J(1))+[1,BLANK],'>'),
          ('A',mkrun((1,0),J(3),1)+[1,1,BLANK],R4,'>'))
PH['L3']=(('A',[1,1,BLANK],[0]+mkrun(ONE6,J(1))+[1,1,1,1,BLANK],'>'),
          ('A',[1,0,1,1,1,0]+mkrun((1,0),J(3),3)+[1,1,BLANK],R4,'>'))
PH['R0']=(('A',[1,1,1,0,1,0]+Lv,[0]+mkrun(ONE6,J(1))+[1,1,1,1,BLANK],'>'),
          ('A',mkrun((1,0),J(3),4)+[1,1,1,0]+Lv,R4,'>'))
PH['R0e']=(('A',[1,1,1,0,1,1,BLANK],[0]+mkrun(ONE6,J(1))+[1,1,1,1,BLANK],'>'),
          ('A',mkrun((1,0),J(3),4)+[1,1,1,1,BLANK],R4,'>'))
PH['Fin']=(('A',[1,1,1,1,BLANK],[0]+mkrun(ONE6,J(1))+[1,1,1,1,BLANK],'>'),
          ('A',[BLANK],[0]+[1]*9+mkrun(ONE6,J(1))+[1,1,1,1,BLANK],'>'))
if __name__=="__main__":
    for w in sys.argv[1:]:
        s,t=PH[w]
        drive(w,s,t,matchers=[m_TRF],maxev=200,verbose=True)
