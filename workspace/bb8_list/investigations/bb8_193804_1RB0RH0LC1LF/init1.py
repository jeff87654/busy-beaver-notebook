from tmlit import Sim, ST
from trace8 import match
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
n=0
while s.steps<9000:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        lo,hi=s.bounds()
        w=''.join(map(str,s.tape[lo:s.pos+1]))
        m=match(w)
        if m: print(s.steps,m)
