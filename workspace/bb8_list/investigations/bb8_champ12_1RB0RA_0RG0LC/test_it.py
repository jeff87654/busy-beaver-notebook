import sys,os
from genc import *
which=sys.argv[1]
pl.set_tm(phc.TMS[which])
U=phc.U;UR=phc.UR;CTX=phc.CTX
start=('F',[1]+mkrun(U,{'k':1},1)+[V('l')],[0]+mkrun(UR,{'m':1})+CTX+[BLANK],'>')
target=('F',[1]+mkrun(U,{'k':1})+[V('l')],[0]+mkrun(UR,{'m':1},2)+CTX+[BLANK],'>')
body=proof_text('IT',start,target)
head=open('headc.v.in').read().replace('@TABLE@',table(phc.TMS[which])).replace('@TM@',phc.TMS[which])
open('scratch_it.v','w').write(head+crossings()+'\n'+body)
