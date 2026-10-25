import sys
def parse(s):
    T={}
    for i,blk in enumerate(s.split("_")):
        for r in (0,1):
            t=blk[3*r:3*r+3]
            T[(i,r)]=None if t[0]=="-" else (int(t[0]),1 if t[1]=="R" else -1,ord(t[2])-65)
    return T
N=int(sys.argv[2]); bad=0; n=0
for ln in open(sys.argv[1]):
    m,st=ln.split()[:2]; T=parse(m); tape=bytearray(2*N+3); p=N+1; s=ord(st)-65; n+=1
    for k in range(N):
        t=T[(s,tape[p])]
        if t is None: print("HALT",m,st,k); bad+=1; break
        tape[p]=t[0]; p+=t[1]; s=t[2]
print(n,"rows,",bad,"halted within",N)
