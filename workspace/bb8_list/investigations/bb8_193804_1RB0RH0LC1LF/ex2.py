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
for i in range(900):
    s.step()
    if i>=500 and s.state!=2 or True:
        pass
    if i>=500:
        p=s.pos
        # require dense region to the left: need P cells
        xs=[s.tape[p-j] for j in range(P)]
        behind=[s.tape[p+1+j] for j in range(depthmax)]
        lm,why=pl.derive_crossing(ST[s.state],'<',xs,behind)
        if lm: print(i,ST[s.state],"p",p,"OK",lm["ys"],lm["ctx"])
        elif i%37==0: print(i,ST[s.state],why[:100])
print('---reasons')
