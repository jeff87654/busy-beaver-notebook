import sys
from lit import parse,M
T=parse(M)
def trace(st,s=2,maxn=400,every=1,stop_evt=True):
    tape={i:int(c) for i,c in enumerate(st)};p=0;n=0;lo=0
    while n<maxn:
        lo=min(lo,p);hi=max(max(tape),p)
        row=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
        if n%every==0: print(n,'ABCDEFGH'[s],row[:p-lo]+'['+row[p-lo:p-lo+1]+']'+row[p-lo+1:])
        v=tape.get(p,0);r=T[(s,v)]
        if r is None: print('HALT');break
        tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2];n+=1
        if stop_evt and p<lo and s==2 and n>1: print(n,'EVENT C',''.join(str(tape.get(i,0)) for i in range(p,max(tape)+1)));break
if __name__=='__main__':
    trace(sys.argv[1],maxn=int(sys.argv[2]))
