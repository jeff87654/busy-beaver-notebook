import idle, sys
from sim import T
# trace.py s0 s1 : print every step between s0 and s1 (cells, with alignment marks every 2 cells relative to even positions)
s0=int(sys.argv[1]);s1=int(sys.argv[2])
tape={};pos=0;q=0;lo=hi=0
for s in range(s1):
    if s>=s0:
        a=lo-(lo%2); 
        st=''
        for i in range(a,hi+3):
            if i%2==0: st+=' '
            st+=('['+'ABCDEFG'[q] if i==pos else '')+str(tape.get(i,0))+(']' if i==pos else '')
        print(s,st)
    b=tape.get(pos,0);tr=T[(q,b)]
    tape[pos]=tr[0];pos+=tr[1];q=tr[2];lo=min(lo,pos);hi=max(hi,pos)
