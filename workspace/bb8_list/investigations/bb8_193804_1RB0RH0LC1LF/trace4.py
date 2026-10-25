import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
start=int(sys.argv[1]); cnt=int(sys.argv[2])
lastd=0; lastturn=0; ev=0
while ev<cnt:
    q=s.state; sym=s.tape[s.pos]
    d=s.T[q][sym][1]
    if d!=lastd and s.steps>=start:
        lo,hi=s.bounds()
        # local context
        L=''.join(map(str,s.tape[s.pos-8:s.pos])); R=''.join(map(str,s.tape[s.pos:s.pos+9]))
        print(s.steps,'turn',ST[q],sym,'dir',d,'pos-lo',s.pos-lo,'hi-pos',hi-s.pos,L,'|',R, 'since',s.steps-lastturn)
        lastturn=s.steps; ev+=1
    lastd=d
    s.step()
