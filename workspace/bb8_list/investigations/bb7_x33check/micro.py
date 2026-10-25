import idle, sys
from sim import parse, X
# print tape at each change of state (macro trace), starting from K(ds;b)
ds=list(map(int,sys.argv[1].split(','))) if sys.argv[1] else []; b=int(sys.argv[2]); maxs=int(sys.argv[3])
T=parse(X); tape={}; p=0
for d in ds:
    for _ in range(d): tape[p]=1; p+=1
    tape[p]=0; p+=1
for _ in range(b): tape[p]=1; p+=1
pos=p; st=0; prev=None; n=0
def show():
    lo=min([k for k in tape if tape[k]]+[pos]); hi=max([k for k in tape if tape[k]]+[pos])
    s=''
    for i in range(lo-1,hi+2):
        c=str(tape.get(i,0))
        s+= f'[{"ABCDEFG"[st]}{c}]' if i==pos else c
    return s
while n<maxs:
    sym=tape.get(pos,0); tr=T[(st,sym)]
    if (st,sym)!=prev: print(f'{n:6d} {"ABCDEFG"[st]}{sym} {show()}')
    prev=(st,sym)
    if tr is None: print('HALT'); break
    w,d,ns=tr; tape[pos]=w; pos+=d; st=ns; n+=1
    if st==0 and pos>max(k for k in tape if tape[k]): print(f'{n:6d} K {show()}'); break
