import idle, random, sys
import pb2
from pb2 import show, comp
pb2.SS=''
import os
if os.environ.get('ASS'): pb2.SS=os.environ['ASS']
# Family A: state as raw bit string w (left part incl. a,y), u=10 s=0, alt sep '1', S='-'. canonical runs via greedy parse.
def to_bits(runs,seps):
    w='10'*runs[0]
    for s,r in zip(seps,runs[1:]): w+=('0' if s==' ' else '1')+'10'*r
    return w
def parse(w):
    runs=[];seps=[];cur=0;i=0
    while i<len(w):
        if w.startswith('10',i): cur+=1;i+=2
        elif w[i]=='0': runs.append(cur);seps.append(' ');cur=0;i+=1
        else: runs.append(cur);seps.append('|');cur=0;i+=1
    runs.append(cur)
    # strip leading empty runs separated by '0' (blank)
    while len(runs)>1 and runs[0]==0 and seps[0]==' ': runs.pop(0);seps.pop(0)
    return runs,seps
def astep(runs,seps):
    runs=list(runs);seps=list(seps)
    while len(runs)<3: runs=[0]+runs; seps=[' ']+seps
    y=runs[-1]; a=runs[-2]
    if a!=0 or seps[-1]!=' ' or seps[-2]!=' ': return None,'NOTMOMENT'
    D=runs[:-2]; DS=seps[:-2]   # digits, DS[j] = sep before D[j+1]
    if not D or all(d==0 for d in D) and all(s==' ' for s in DS):
        if y%2 or y<4: return None,'EMPTYSMALL'
        return [1]+[2]*(y//2-1)+[0,6],[' ']*(y//2-1)+[' ',' ']
    if D[-1]>=2:
        if D[-1]%2: return None,'LASTODD'
        D[-1]-=2; return D+[0,2*y+6],DS+[' ',' ']
    if D[-1]==1: return None,'LAST1'
    i=len(D)-1
    while i>=0 and D[i]==0:
        if i>0 and DS[i-1]=='|': return None,'ALTZERO'
        i-=1
    K=len(D)-1-i
    if i<0: return [1]+[2]*(y//2-1)+[0,6],[' ']*(y//2-1)+[' ',' ']  # blank to the left
    if D[i]>=2:
        v=y+2-2*K
        if v<2: return None,'SMALL'
        D[i]-=2
        D=D[:i+1]+[v]+[2]*(K-1); return D+[0,6],DS[:i]+[' ']*K+[' ',' ']
    # D[i]==1: TOP-ACC
    c=y-1-2*K
    if c<1: return None,'SMALLTOP'
    if i>0 and DS[i-1]=='|':
        D[i-1]+=1+c; D=D[:i]+[2]*K; DS2=DS[:i-1]+['|']+[' ']*(K-1)
    else:
        D[i]=c; D=D[:i+1]+[2]*K; DS2=DS[:i]+['|']+[' ']*(K-1)
    return D+[0,6],DS2+[' ',' ']
def canon(runs,seps):
    runs,seps=parse(to_bits(runs,seps))
    while True:
        if len(runs)<3: runs=[0]*(3-len(runs))+runs; seps=[' ']*(len(runs)-1-len(seps))+seps
        if runs[-2]>0 and seps[-1]==' ':
            runs[-1]+=2*runs[-2]; runs[-2]=0; runs,seps=parse(to_bits(runs,seps)); continue
        D=runs[:-2]
        if all(d==0 for d in D) and all(x==' ' for x in seps[:-1]):
            y=runs[-1]; runs=[1]+[2]*(y//2-1)+[0,6]; seps=[' ']*(len(runs)-1); continue
        return runs,seps
def fmt(runs,seps):
    o=str(runs[0])
    for s,r in zip(seps,runs[1:]): o+=s+str(r)
    return comp(o)
if __name__=='__main__':
    M,O,Q=sys.argv[1:4]; n=int(sys.argv[4]); ymin=int(sys.argv[5]) if len(sys.argv)>5 else 10
    random.seed(9); st={}
    for it in range(n):
        L=random.randint(0,5)
        D=[random.choice([0,0,2,4,6,8]) for _ in range(L)]
        DS=[' ']*max(0,L-1)
        # optionally one odd run / alt sep
        if L>=1 and random.random()<0.5:
            j=random.randrange(L); D[j]=random.choice([1,1,3,5,7]) 
        if L>=2 and random.random()<0.3:
            j=random.randrange(L-1); DS[j]='|'
        y=2*random.randint(ymin//2,ymin//2+15)
        runs,seps=canon(D+[0,y],DS+[' ',' '])
        a=astep(runs,seps)
        if a[0] is None:
            st[a[1]]=st.get(a[1],0)+1
            if a[1] in ('SMALL','SMALLTOP','EMPTYSMALL'):
                lit=show(M,O,Q,'P:'+to_bits(runs,seps)+' 0',10**7,1,4)[0]; k=a[1]+('-H' if lit.startswith('H') else '-K'); st[k]=st.get(k,0)+1
            continue
        exp=fmt(*canon(*a))
        lit=show(M,O,Q,'P:'+to_bits(runs,seps)+(' 0' if pb2.SS=='' else ' 0'),10**8,1,4)[0]
        got=lit.split(' : ')[1] if ' : ' in lit else lit
        if lit.startswith('H'): print('HALT-in-OKcase',fmt(runs,seps))
        k='OK' if got==exp else 'MISMATCH'
        st[k]=st.get(k,0)+1
        if k!='OK': print('MISMATCH',fmt(runs,seps),'exp',exp,'lit',lit)
    print(st)
