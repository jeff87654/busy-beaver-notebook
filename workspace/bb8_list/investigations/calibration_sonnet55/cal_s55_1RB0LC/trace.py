import sys
exec(open('ev.py').read().split("N=int")[0])
SZ=1<<24
tape=bytearray(SZ); p=SZ//2; q=0
def rl():
    idx=[i for i in range(SZ//2-10,SZ//2+2000000) if tape[i]]
    a=min(idx+[p]); b=max(idx+[p]); out=[]; i=a
    while i<=b:
        if i==p: out.append("[%s]%d"%("ABCDEFGH"[q],tape[i])); i+=1; continue
        j=i
        while j<=b and j!=p and tape[j]==tape[i]: j+=1
        out.append("%d^%d"%(tape[i],j-i) if j-i>1 else str(tape[i])); i=j
    return " ".join(out)
t0=int(sys.argv[1]); t1=int(sys.argv[2]); states=sys.argv[3]
lastq=-1
for t in range(t1):
    if t>=t0 and "ABCDEFGH"[q] in states and (lastq!="ABCDEFGH"[q] or True):
        print(t,rl())
    r=tb[q*2+tape[p]]
    tape[p]=r[0]; p+=r[1]; q=r[2]
