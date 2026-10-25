import sys; from sim import *
T=parse(M1); tape={}; h=0; s=0; step=0
A,B=int(sys.argv[1]),int(sys.argv[2])
while step<B:
    b=tape.get(h,0); t=T[(s,b)]
    if t is None: print('halt',step); break
    tape[h]=t[0]; h+=t[1]; s=t[2]; step+=1
    if step>=A:
        st,lo=show(tape,h,s)
        print(step, st[:90])
