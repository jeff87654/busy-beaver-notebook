import idle, sys
from lit import parse
def seq(m,N):
    T=parse(m); tape={}; p=0; q=0; ones=0; out=[]
    for st in range(N):
        c=tape.get(p,0); tr=T[(q,c)]
        if tr is None: out.append(-1); break
        w,d,nq=tr; ones+=w-c; tape[p]=w; p+=d; q=nq; out.append(ones)
    return out
a=seq(sys.argv[1],int(sys.argv[3])); b=seq(sys.argv[2],int(sys.argv[3]))
off=[k for k in range(0,40) if a[k:k+5000]==b[0:5000] or b[k:k+5000]==a[0:5000]]
print('equal' if a==b else 'differ', 'offsets',off, a[:30], b[:30])
