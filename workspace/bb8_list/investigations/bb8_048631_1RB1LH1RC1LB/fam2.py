from sim import *
import sys,re
def cfg(k,m): return '01011'+'001'*k+'01'+'1'*m+'0011'
def run_from(st,N,show=True,state=1):
    t=parse(M);tape={i:int(c) for i,c in enumerate(st)};p=0;s=state;lo=0;hi=len(st)-1
    for i in range(N):
        r=t[(s,tape.get(p,0))]
        if r is None: return ('HALT',i)
        tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
        lo=min(lo,p);hi=max(hi,p)
        if p<=lo and s==1 and show:
            x=''.join(str(tape.get(q,0)) for q in range(lo,hi+1))
            m=re.fullmatch(r'01011((?:001)*)01(1*)0011',x)
            print(i+1,(len(m.group(1))//3,len(m.group(2))) if m else re.sub(r'(.)\1*',lambda z:z.group(1)+'^'+str(len(z.group(0)))+' ',x))
    return ('run',N)
if __name__=="__main__":
    print(run_from(cfg(int(sys.argv[1]),int(sys.argv[2])),int(sys.argv[3])))
