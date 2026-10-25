import sys
from lit import *
# start config: L tape-order string, R string (head at R[0]), state
L=sys.argv[1]; R=sys.argv[2]; st=sys.argv[3]; n=int(sys.argv[4])
w='0000'+L+R+'000000'
s=Sim.from_word(TM,w,4+len(L),st,1<<10)
base=s.pos-4-len(L)
for i in range(n+1):
    t=''.join(str(s.tape[j]) for j in range(base,base+len(w)))
    p=s.pos-base
    print('%4d %s[%s]%s'%(i,t[:p],ST[s.state],t[p:].rstrip('0')))
    if not s.step(): print('HALT'); break
