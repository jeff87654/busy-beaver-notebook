import idle, sys
from lit import parse
# prints run lists (runs of 1s separated by single 0s) at moments: state Q, head on blank right of tape, tape ends with '0', and x(=run[-2])==0
def runs_of(strg):
    # strg starts with 1, ends with 0 (S). runs separated by single zeros
    assert strg.endswith('0')
    body=strg[:-1]
    return [len(t) for t in body.split('0')]
def comp(r):
    o=[];i=0
    while i<len(r):
        j=i
        while j<len(r) and r[j]==r[i]: j+=1
        o.append(str(r[i])+('x%d'%(j-i) if j-i>1 else '')); i=j
    return ' '.join(o)
def run(m,O,Q,N,maxout=200,every=False):
    T=parse(m); s=-1 if O=='L' else 1
    tape=bytearray(1<<22); off=1<<21; p=off; q=0; lo=hi=p; out=0
    for st in range(N):
        c=tape[p]; tr=T[(q,c)]
        if tr is None:
            print('H',st,sum(tape)); return
        w,d,nq=tr; tape[p]=w
        if w: lo=min(lo,p); hi=max(hi,p)
        p+=d; q=nq
        if q==Q and tape[p]==0 and tape[p-s]==0 and tape[p-2*s]==1:
            if (s==1 and hi<p) or (s==-1 and lo>p):
                seg=tape[lo:p] if s==1 else tape[p+1:hi+1][::-1]
                strg=bytes(x+48 for x in seg).decode().lstrip('0')
                r=runs_of(strg)
                if every or (len(r)>=2 and r[-2]==0):
                    print(st+1,'|',comp(r)); out+=1
                    if out>=maxout: return
    print('END',N)
if __name__=='__main__':
    run(sys.argv[1],sys.argv[2],ord(sys.argv[3])-65,int(sys.argv[4]),int(sys.argv[5]),len(sys.argv)>6)
