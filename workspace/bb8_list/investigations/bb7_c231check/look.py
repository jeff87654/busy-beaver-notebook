import sys; from sim import *
T=parse(M1); tape={}; h=0; s=0; step=0
marks=set(int(x) for x in sys.argv[1:])
while step<max(marks):
    b=tape.get(h,0); t=T[(s,b)]
    if t is None: print('halt',step); break
    tape[h]=t[0]; h+=t[1]; s=t[2]; step+=1
    if step in marks: print(step, show(tape,h,s)[0])
