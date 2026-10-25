import sys,re
from lit import parse,M
t=parse(M);tape={};p=0;s=0;lo=0
N=int(sys.argv[1]);out=0
def rle(st):
    # compress periodic (001)/(100) runs
    st=re.sub(r'((?:100)+)',lambda m:'(100)^%d'%(len(m.group(1))//3),st)
    st=re.sub(r'((?:001)+)',lambda m:'(001)^%d'%(len(m.group(1))//3),st)
    st=re.sub(r'1{4,}',lambda m:'1^%d'%len(m.group(0)),st)
    return st
for k in range(N):
    v=tape.get(p,0);r=t[(s,v)]
    if r is None: print("HALT",k);break
    tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
    if p<lo:
        lo=p
        if s==2:
            st=''.join(str(tape.get(i,0)) for i in range(lo,max(tape)+1))
            print(k+1,'C',rle(st))
