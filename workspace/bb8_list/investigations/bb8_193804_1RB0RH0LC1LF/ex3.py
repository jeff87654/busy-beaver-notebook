import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
start=int(sys.argv[1])
prev=0
while True:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>=start and gap>500: break
snap=[]
for i in range(1200):
    s.step()
    p=s.pos
    snap.append((i,s.state,p,tuple(s.tape[p-12:p])+('H',)+tuple(s.tape[p:p+12])))
# find recurrences in window sense
byw={}
for i,q,p,w in snap:
    if i<400: continue
    byw.setdefault((q,w),[]).append((i,p))
for k,v in byw.items():
    if len(v)>1: print(ST[k[0]],v)
