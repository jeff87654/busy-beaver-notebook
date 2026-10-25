import sys
M="1RB1RD_1LC1LF_1RH1RA_1LE1LG_0RB1LE_1RC0LG_1RA0LB_---1RF"
def parse(m):
    t={}
    for i,s in enumerate(m.split('_')):
        for b in (0,1):
            x=s[3*b:3*b+3]
            t[(i,b)]=None if x=='---' else (int(x[0]),x[1],'ABCDEFGH'.index(x[2]))
    return t
def run(n,snap=()):
    t=parse(M);tape={};p=0;s=0
    for k in range(n):
        v=tape.get(p,0)
        r=t[(s,v)]
        if r is None: print("HALT",k,s,v);return
        tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
        if s==7 and tape.get(p,0)==0 or k+1 in snap:
            pass
        if k+1 in snap: show(tape,p,s,k+1)
    show(tape,p,s,n)
def show(tape,p,s,k):
    lo=min(tape);hi=max(tape)
    st=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
    print(k,'ABCDEFGH'[s],'pos',p-lo,'len',len(st),'ones',sum(tape.values()));print(st)
if __name__=="__main__":
    run(int(sys.argv[1]),set(int(x) for x in sys.argv[2:]))
