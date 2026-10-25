import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM)
n=int(sys.argv[1]); cnt=0
prev=0
while s.steps<n:
    if not s.step(): print('HALT',s.steps,s.last); break
    if ST[s.state]=='C' and s.tape[s.pos]==0 and s.pos==s.hi+0 or (ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1])):
        lo,hi=s.bounds()
        w=''.join(map(str,s.tape[lo:s.pos]))
        print(s.steps, s.steps-prev, w); prev=s.steps; cnt+=1
        if cnt>int(sys.argv[2]): break
