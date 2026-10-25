import sys,re
from lit import Sim, MAIN, rle
def summ(s):
    return re.sub(r'(?:0\^2 1 ){3,}0\^2 1', lambda m:'(0^2 1)^%d'%((m.group(0).count('0^2 1'))), s)
def run(word, maxsteps=5000000, tm=MAIN):
    s=Sim(tm,size=1<<16)
    base=s.pos
    for i,c in enumerate(word):
        s.tape[base+1+i]=int(c)
    s.hi=base+len(word); 
    while s.steps<maxsteps:
        lo0=s.lo
        if not s.step():
            return ('HALT',s.steps,s.show())
        if s.pos<lo0 and s.state==0:
            t=s.tape;hi=s.hi
            while hi>s.pos and t[hi]==0:hi-=1
            w=''.join(map(str,t[s.pos+1:hi+1]))
            return ('A',s.steps,summ(rle(w)))
    return ('TO',s.steps,'')
if __name__=='__main__':
    j=int(sys.argv[1])
    for n in range(2,int(sys.argv[2]),2):
        w='1'*n+('000'+'1'*j if j else '')
        print(n,n%6,run(w))
