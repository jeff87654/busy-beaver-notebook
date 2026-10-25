import sys
sys.path.insert(0,'.')
import planner8 as pl
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
pl.set_tm(TM)
s=Sim(TM,1<<20)
start=int(sys.argv[1]); P=int(sys.argv[2]); depthmax=int(sys.argv[3])
prev=0
while True:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>=start and gap>500: break
mn=s.pos; n=0
res=[]
for i in range(1500):
    s.step()
    if s.pos<mn:
        mn=s.pos
        p=s.pos
        xs=[s.tape[p-j] for j in range(P)]
        behind=[s.tape[p+1+j] for j in range(depthmax)]
        if i>300:
            lm,why=pl.derive_crossing(ST[s.state],'<',xs,behind)
            print(i,p,ST[s.state],'OK '+str(lm['ys'])+' ctx '+str(lm['ctx']) if lm else why[:90])
