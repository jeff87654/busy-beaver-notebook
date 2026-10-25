import sys
M="1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA"
tb=[]
for ch in M.split("_"):
    for s in (0,1):
        e=ch[3*s:3*s+3]
        tb.append(None if e=="---" else (int(e[0]),1 if e[1]=="R" else -1,ord(e[2])-65))
N=int(sys.argv[1]); SZ=1<<24
tape=bytearray(SZ); p=SZ//2; q=0; lo=p  # lo = leftmost cell ever nonzero-or-visited? use leftmost 1 tracking
left=p  # leftmost visited
def rle(a,b):
    out=[];i=a
    while i<=b:
        j=i
        while j<=b and tape[j]==tape[i]: j+=1
        out.append("%d^%d"%(tape[i],j-i)); i=j
    return " ".join(out)
lastp=None
for t in range(N):
    if p<left:
        left=p
        # new leftmost visited cell
        if len(sys.argv)>2:
            hi=max(i for i in range(left,min(SZ,p+3000000)) if tape[i]) if False else None
    r=tb[q*2+tape[p]]
    if r is None: print("HALT",t,q); break
    tape[p]=r[0]; p+=r[1]; q=r[2]
    if p<left:
        left=p
        print(t,"ABCDEFGH"[q],"left=",p-SZ//2)
