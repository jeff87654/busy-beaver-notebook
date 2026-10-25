import sys
exec(open('ev.py').read().split("N=int")[0])
def parse_left(s):
    # s string of left part (leftmost nonblank..head-1). digits: runs of 1 separated by single 0. returns tuple or None
    if s=="": return ()
    if s[-1]!='1' and True: return None
    parts=s.split('0')
    if any(x=="" for x in parts): 
        return None
    return tuple(len(x) for x in parts)
def nextD(ds,y,N=2000000):
    left="".join(("1"*d)+"0" for d in ds)[:-1] if ds else ""
    SZ=1<<20; tape=bytearray(SZ); p=SZ//2; q=0
    L=[int(c) for c in left]
    for i,b in enumerate(reversed(L)): tape[p-1-i]=b
    for i in range(y): tape[p+1+i]=1
    lo=p-len(L); hi=p+y
    for t in range(N):
        if t>0 and q==0 and tape[p]==0 and tape[p+1]==1:
            j=p+1
            while tape[j]: j+=1
            if j>hi and True:
                s="".join(map(str,tape[lo:p]))
                s=s.lstrip('0')
                d=parse_left(s)
                if d is not None: return t,d,j-p-1
        r=tb[q*2+tape[p]]
        if r is None: return t,"HALT","ABCDEFGH"[q]+str(tape[p])
        tape[p]=r[0]; p+=r[1]; q=r[2]
        if p<lo:lo=p
        if p>hi:hi=p
    return None
if __name__=="__main__":
    import itertools
    for ds in [(),(1,),(2,),(3,),(4,),(1,1),(2,1),(1,2),(5,)]:
        for y in range(1,13):
            print(ds,y,nextD(ds,y,300000))
