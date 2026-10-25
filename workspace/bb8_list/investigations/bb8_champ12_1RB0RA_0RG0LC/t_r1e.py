import sys
from genc import *
import matchers as M
pl.set_tm(phc.TMS['1'])
U=phc.U;UR=phc.UR;CTX=phc.CTX
M.reset()
N=int(sys.argv[1])
start=('B',phc.SUF+[0,1]*N+mkrun(U,{'n':1})+[0,1,1]+[0,1]*3+mkrun(U,{'q':1})+[0,1,1,V('l')],[BLANK],'>')
script,cfg=drive('R1',start,None,matchers=(M.m_LN1,),maxev=80)
print(M.EQS)
