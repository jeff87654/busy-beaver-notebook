import sys
exec(open('ev.py').read().split("N=int")[0])
N=int(sys.argv[1]); SZ=1<<24
tape=bytearray(SZ); p=SZ//2; q=0; left=p
def rle():
    nz=[i for i in range(SZ) if tape[i]] if False else None
    a=left; b=max(i for i in range(left,left+400000) if i<SZ and tape[i]) if False else None
def show(t):
    idx=[i for i in range(SZ//2-50,SZ//2+3000000) if tape[i]]
    a=min(idx+[p]); b=max(idx+[p])
    out=[];i=a
    while i<=b:
        j=i
        while j<=b and tape[j]==tape[i] and j!=p and (i!=p): j+=1
        if i==p: j=i+1
        out.append(("[%s]"%"ABCDEFGH"[q] if i==p else "")+"%d^%d"%(tape[i],j-i)); i=j
    print(t,"ABCDEFGH"[q]," ".join(out))
S=set(int(x) for x in sys.argv[2:])
for t in range(N+1):
    if t in S: show(t)
    r=tb[q*2+tape[p]]
    if r is None: print("HALT",t,q); break
    tape[p]=r[0]; p+=r[1]; q=r[2]
