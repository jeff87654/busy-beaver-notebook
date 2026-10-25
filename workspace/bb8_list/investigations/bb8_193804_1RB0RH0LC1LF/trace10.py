import sys
from tmlit import Sim, ST
from trace8 import match
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
start=int(sys.argv[1]); nst=int(sys.argv[2])
prev=0
while True:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>=start and gap>500: break
base=s.pos
for i in range(nst):
    lo,hi=s.bounds()
    row=''.join('.' if c==0 else '1' for c in s.tape[base-60:base+4])
    mark=' '*(s.pos-(base-60))+'^'
    print('%3d %s'%(i,ST[s.state]),row); print('    ',' '+mark) if False else None
    print('     '+mark)
    s.step()
