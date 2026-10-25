import sys
from tmlit import Sim, ST
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
s=Sim(TM,1<<20)
a=int(sys.argv[1]); cnt=int(sys.argv[2])
prev=0; n=0
def fac(w,p=17):
    best=(0,0)
    for i in range(0,p):
        # periodic run starting at i
        j=i
        while j+p<=len(w) and w[j:j+p]==w[i:i+p]: j+=p
        k=(j-i)//p
        if k>best[0]: best=(k,i)
    k,i=best
    return w[:i],w[i:i+p],k,w[i+p*k:]
while n<cnt:
    s.step()
    if ST[s.state]=='C' and s.tape[s.pos]==0 and not any(s.tape[s.pos+1:s.hi+1]):
        gap=s.steps-prev; prev=s.steps
        if s.steps>a:
            lo,hi=s.bounds()
            w=''.join(map(str,s.tape[lo:s.pos])).replace('0','.')
            pre,body,k,post=fac(w)
            print(s.steps,gap,'|',pre,'|',body,'^',k,'|',post); n+=1
