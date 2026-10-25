import sys
sys.path.insert(0,'.')
import planner8 as pl
from pipe import derive_pipe
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
pl.set_tm(TM)
s=Sim(TM,1<<20)
start=int(sys.argv[1]); P=17; NC=int(sys.argv[2])
prev=0
while True:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>=start and gap>500: break
mn=s.pos; mx=s.pos; phase=0
for i in range(6000):
    q=s.state
    s.step()
    # left crawl: record minima
    if s.pos<mn and i<1500:
        mn=s.pos; p=s.pos
        xs=[s.tape[p-j] for j in range(P)]
        c=[s.tape[p+1+j] for j in range(NC)]
        if i>400:
            lm,why=derive_pipe(ST[s.state],'<',xs,c)
            print('crawl',i,ST[s.state],('OK ys=%s'%''.join(map(str,lm['ys']))) if lm else why[:80])
