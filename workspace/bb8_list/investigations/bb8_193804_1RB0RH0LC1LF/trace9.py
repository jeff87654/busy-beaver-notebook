import sys
from tmlit import Sim, ST
from trace8 import match
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
start=int(sys.argv[1])
prev=0
while True:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>=start and gap>500: break
def dump(tag):
    lo,hi=s.bounds()
    t=''.join(map(str,s.tape[lo:hi+1])).replace('0','.')
    print(tag,s.steps,ST[s.state],'pos',s.pos-lo,'len',hi-lo+1); print(t)
dump('start')
pos0=s.pos
# run until the head hits the left end for the first time (leftmost cell reached)
lo0=min(i for i in range(s.lo,s.hi+1) if s.tape[i])
mn=s.pos; 
while True:
    s.step()
    if s.pos<lo0-1: break
dump('at left end')
for k in range(int(sys.argv[2])):
    s.step()
dump('later')
