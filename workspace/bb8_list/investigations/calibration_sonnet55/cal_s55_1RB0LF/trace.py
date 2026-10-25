import sys
from lit import Sim,MAIN
w=sys.argv[1]; N=int(sys.argv[2])
s=Sim(MAIN,size=1<<12); b=s.pos
for i,c in enumerate(w): s.tape[b+1+i]=int(c)
s.hi=b+len(w)
print(s.steps, s.show(False))
for _ in range(N):
    if not s.step(): print('halt');break
    print(s.steps, s.show(False))
