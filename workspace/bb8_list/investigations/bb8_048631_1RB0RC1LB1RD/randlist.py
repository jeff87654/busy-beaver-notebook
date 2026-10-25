import sys,re,random
from sim1 import T
def build(a,ts):
    w='10'*a+'11'+'0'*(2*a+3)+'1'
    for t in ts: w+='0'*(2*t-1)+'1'
    return w
def parse(tape):
    hi=max(k for k,v in tape.items() if v)
    st=''.join(str(tape.get(i,0)) for i in range(0,hi+1))
    lo=min(k for k,v in tape.items() if v)
    if lo<0: return None
    rl=[(len(x),len(y)) for x,y in re.findall('(1+)(0*)',st)]
    k=0
    while k<len(rl) and rl[k]==(1,1): k+=1
    rest=rl[k:]
    if rest and rest[0][0]==2 and k>=2 and rest[0][1]==2*k+3 and all(x==1 for x,y in rest[1:]) and all(y%2==1 for x,y in rest[1:-1]) and rest[-1]==(1,0):
        return (k,tuple((y+1)//2 for x,y in rest[1:-1]))
    return None
def run(a,ts,maxsteps=2000000):
    tape={}
    w=build(a,ts)
    for i,ch in enumerate(w):
        if ch=='1': tape[i]=1
    pos=-2;q=7
    first=True
    for step in range(maxsteps):
        s=tape.get(pos,0)
        if pos==-2 and q==7 and not first:
            r=parse(tape)
            if r is not None: return ('std',r,step)
        first=False
        tr=T[(q,s)]
        if tr is None: return ('HALT',step,None)
        wr,d,nq=tr
        tape[pos]=wr; pos+=1 if d=='R' else -1; q=nq
    return ('timeout',None,maxsteps)
if __name__=='__main__':
    random.seed(int(sys.argv[1]))
    from collections import Counter
    res=Counter()
    for trial in range(int(sys.argv[2])):
        a=random.choice([2,3,3,3,4,5,6])
        k=random.randint(0,4)
        ts=tuple(random.choice([1,2,2,3,4,5,6,7,8]) for _ in range(k))
        r=run(a,ts)
        res[r[0]]+=1
        if r[0]!='std' or trial<12: print(a,ts,'->',r)
    print(res)
