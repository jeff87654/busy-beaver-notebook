import sys
from fam import *
from kw import word
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RH1LG_0RG1LD_0RH0RF'
tm=parse_tm(M)
def rle(w):
    out=[];i=0
    while i<len(w):
        j=i
        while j<len(w) and w[j]==w[i]: j+=1
        out.append(w[i]+('' if j-i==1 else '^%d'%(j-i)))
        i=j
    return ' '.join(out)
def run(w,maxsteps,show=40,q=1):
    n=1<<22
    t=bytearray(n); p=n//2; base=p-len(w)
    for i,ch in enumerate(w): t[base+i]=ord(ch)-48
    p=base+len(w); st=0; maxp=p; cnt=0
    while st<maxsteps:
        r=tm[(q,t[p])]
        if r is None: print('HALT',st); return
        wr,d,nq=r; t[p]=wr; p+=d; q=nq; st+=1
        if p>maxp and q==1:
            maxp=p
        if q==1 and t[p]==0 and p>=maxp:
            # B at the frontier
            lo=0
            while not t[lo]: lo+=1
            s=''.join(chr(48+t[i]) for i in range(lo,p))
            cnt+=1
            if cnt<=show: print(st,len(s),rle(s))
    print('end',st,'p',p-base,'state',q)
if __name__=='__main__':
    ds=eval(sys.argv[1]);a=int(sys.argv[2]);b=int(sys.argv[3]);N=int(sys.argv[4])
    run(word(ds,a,b),N,show=int(sys.argv[5]) if len(sys.argv)>5 else 40)
