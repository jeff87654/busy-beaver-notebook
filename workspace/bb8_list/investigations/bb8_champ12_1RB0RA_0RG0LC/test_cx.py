import sys
from genc import *
pl.set_tm(phc.TMS['1'])
U=phc.U;UR=phc.UR;CTX=phc.CTX
start=('F',[1,1]+mkrun(U,{'q':1},4)+[1,V('l')],[0]+mkrun(UR,{'m':1})+CTX+[BLANK],'>')
try: drive('MID',start,None,maxev=9,verbose=False)
except RuntimeError: pass
head=open('headc.v.in').read().replace('@TABLE@',table(phc.TMS['1'])).replace('@TM@',phc.TMS['1'])
open('scratch_cx.v','w').write(head+crossings())
print(sorted(pl.LEMMAS))
