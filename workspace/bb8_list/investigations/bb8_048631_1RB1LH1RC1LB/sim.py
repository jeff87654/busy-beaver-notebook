import sys
M="1RB1LH_1RC1LB_0RD1RE_1LB0LB_1RF0LA_1LG1LF_1RH0LD_---0LE"
def parse(m):
    t={}
    for i,x in enumerate(m.split('_')):
        for s in (0,1):
            c=x[3*s:3*s+3]
            t[(i,s)]=None if c=='---' else (int(c[0]),c[1],'ABCDEFGH'.index(c[2]))
    return t
def run(m,n,trace=0):
    t=parse(m);tape={};p=0;s=0;lo=hi=0
    for i in range(n):
        r=t[(s,tape.get(p,0))]
        if r is None: return ('halt',i,tape,p,s)
        tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
        lo=min(lo,p);hi=max(hi,p)
        if trace and i<trace: print(i+1,'ABCDEFGH'[s],''.join(str(tape.get(q,0)) for q in range(lo,hi+1)),p-lo)
    return ('run',n,tape,p,s)
if __name__=="__main__":
    m=sys.argv[1] if len(sys.argv)>1 else M
    r=run(m,int(sys.argv[2]),int(sys.argv[3]) if len(sys.argv)>3 else 0)
    print(r[0],r[1],sum(r[2].values()))
