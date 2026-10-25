import idle
def parse(m):
    rows=m.split('_'); T={}; ns=len(rows)
    for i,r in enumerate(rows):
        for c in range(2):
            t=r[3*c:3*c+3]
            if t[0]=='-' or t[2]=='-' or ord(t[2])-65>=ns: T[(i,c)]=None
            else: T[(i,c)]=(int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
    return T
def trace(m,O,Q,bits,N,every):
    T=parse(m); s=-1 if O=='L' else 1
    tape={}; p=0
    for i,ch in enumerate(bits): 
        if ch=='1': tape[i-len(bits)]=1
    q=ord(Q)-65; out=[]
    for st in range(N):
        tr=T[(q,tape.get(p,0))]
        if tr is None: out.append(('HALT',st,p)); return out
        w,d,q2=tr
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d*s; q=q2
        if st%every==0:
            ks=list(tape); out.append((st,p,min(ks) if ks else 0,max(ks) if ks else 0,len(ks)))
    return out
if __name__=='__main__':
    import sys
    m,O,Q,bits,N,ev=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5]),int(sys.argv[6])
    if bits=='B': bits=''
    for r in trace(m,O,Q,bits,N,ev): print(r)
