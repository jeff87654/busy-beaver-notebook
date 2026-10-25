import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
a=int(sys.argv[1]); cnt=int(sys.argv[2])
prev=0; n=0
while n<cnt:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>a:
            lo,hi=s.bounds()
            print(s.steps,gap,''.join(map(str,s.tape[lo:s.pos])).replace('0','.')); n+=1
