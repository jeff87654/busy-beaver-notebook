import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
marks=[int(x) for x in sys.argv[1:]]
prev=0
for m in marks:
    while s.steps<m:
        if not s.step(): print('HALT'); sys.exit()
    # advance to next C at right end
    while not (ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1])):
        s.step()
    lo,hi=s.bounds()
    w=''.join(map(str,s.tape[lo:s.pos]))
    runs=[len(x) for x in w.split('0')]
    print(s.steps, len(runs), ''.join(map(str,runs)))
