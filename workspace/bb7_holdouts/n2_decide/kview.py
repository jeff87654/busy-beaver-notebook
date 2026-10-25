import idle, sys
from sim import T
# run from blank; at each K-moment (state A, head reads 0, cell right of head... ) print 2-blocks aligned on head
def blocks(tape,pos,lo,hi):
    # align so head is at left cell of a block
    start=pos-((pos-lo)//2)*2-2
    out=[];i=start
    while i<=hi+1:
        out.append(str(tape.get(i,0))+str(tape.get(i+1,0)) if i!=pos else '['+str(tape.get(i,0))+str(tape.get(i+1,0))+']')
        i+=2
    return out
def rl(bl):
    o=[];prev=None;c=0
    for b in bl:
        if b==prev: c+=1
        else:
            if prev is not None: o.append(prev+('^%d'%c if c>1 else ''))
            prev=b;c=1
    o.append(prev+('^%d'%c if c>1 else ''))
    return ' '.join(o)
N=int(sys.argv[1]); every=int(sys.argv[2]) if len(sys.argv)>2 else 1
tape={};pos=0;q=0;lo=hi=0;k=0
for s in range(N):
    b=tape.get(pos,0);tr=T[(q,b)]
    if tr is None: print("HALT",s);break
    tape[pos]=tr[0];pos+=tr[1];q=tr[2];lo=min(lo,pos);hi=max(hi,pos)
    if q==0 and tape.get(pos,0)==0 and tape.get(pos+1,0)==1 and all(tape.get(j,0)==0 for j in range(pos+2,hi+2)):
        k+=1
        if k%every==0: print(s,rl(blocks(tape,pos,lo,hi)))
