import sys
from sim import parse
M='1RB0LD_0RC---_1LC0RD_1LE1LE_0LF1LA_1LG0LG_1RH1RC_1LD1RG'
def enc(L): return ''.join('10'*d+'1' for d in L)
def decl(s):
    L=[];i=0;d=0
    while i<len(s):
        if s.startswith('10',i) and i+2<len(s) or (s.startswith('10',i) and i+2==len(s)): 
            if s[i:i+2]=='10': d+=1;i+=2;continue
        if s[i]=='1': L.append(d);d=0;i+=1;continue
        return None
    return L if d==0 else None
def step(L,m=M,maxn=10**7,minsteps=1):
    """run from K config L (state G, head just left of tape string) until next K config"""
    T=parse(m); s=enc(L); N=len(s)+4*maxn**0 
    off=64; size=len(s)*4+20000
    tape=bytearray(size); pos=off
    for i,ch in enumerate(s): tape[pos+1+i]=1 if ch=='1' else 0
    lo=pos; hi=pos+len(s); st=6
    for n in range(maxn):
        c=tape[pos]
        if (st,c) not in T: return ('H',n+1)
        w,d,q=T[(st,c)]; tape[pos]=w
        if w:
            if pos>hi: hi=pos
            if pos<lo: lo=pos
        pos+=d; st=q
        if pos<=1 or pos>=size-2: return ('T',n)
        if st==6 and tape[pos]==0 and n+1>=minsteps:
            if all(tape[i]==0 for i in range(lo,pos)) :
                while hi>pos and tape[hi]==0: hi-=1
                ss=''.join('1' if x else '0' for x in tape[pos+1:hi+1])
                r=decl(ss)
                if r is not None: return ('K',r,n+1)
    return ('T',maxn)
if __name__=='__main__':
    for line in sys.stdin:
        L=[int(x) for x in line.split()]
        print(L,'->',step(L))
