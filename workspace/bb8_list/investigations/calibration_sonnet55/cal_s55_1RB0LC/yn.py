import sys
exec(open('ev.py').read().split("N=int")[0])
def runY(n,N,verbose=False):
    SZ=1<<22
    tape=bytearray(SZ); p=SZ//2; q=0
    for i in range(n): tape[p+1+i]=1
    left=p; res=[]
    for t in range(N):
        if q==0 and p<=left and tape[p]==0:
            j=p+1
            while tape[j]: j+=1
            k=j-p-1
            if t>0 and tape[p+1] and not any(tape[j:j+50]): return t,"Y(%d)"%k
        r=tb[q*2+tape[p]]
        if r is None: return t,"HALT q=%s"%"ABCDEFGH"[q]
        tape[p]=r[0]; p+=r[1]; q=r[2]
        if p<left:left=p
        if p>SZ-100: return t,"overflow"
    return N,"?"
if __name__=="__main__":
    for n in range(int(sys.argv[1]),int(sys.argv[2])):
        print(n,runY(n,int(sys.argv[3])))
