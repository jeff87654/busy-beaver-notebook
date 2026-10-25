import sys,re
from lit import parse
TM="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
T=parse(TM)
def bl(s):
    out=[]
    for i in range(0,len(s),2):
        b=s[i:i+2]
        if out and out[-1][0]==b: out[-1][1]+=1
        else: out.append([b,1])
    return ' '.join(b if n==1 else f'{b}^{n}' for b,n in out)
def parse_blocks(txt):
    s=''
    for tok in txt.split():
        if '^' in tok:
            b,n=tok.split('^'); s+=b*int(n)
        else: s+=tok
    return s
def run_from(Ls,Rs,st=0,maxsteps=10**7,stop='A',skip=1):
    tape={}
    for i,c in enumerate(Ls): tape[i-len(Ls)]=int(c)
    for i,c in enumerate(Rs): tape[i]=int(c)
    pos=0
    k=0
    while k<maxsteps:
        s=tape.get(pos,0); e=T[(st,s)]
        if e is None: return ('halt',k,tape,pos,st)
        w,d,ns=e; tape[pos]=w; pos+=d; st=ns; k+=1
        if 'ABCDEFGH'[st] in stop and k>=skip:
            return ('stop',k,tape,pos,st)
    return ('max',k,tape,pos,st)
def fmt(res):
    kind,k,tape,pos,st=res
    lo=min(tape); hi=max(tape)
    L=''.join(str(tape.get(i,0)) for i in range(lo,pos))
    if len(L)%2: L='0'+L
    R=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
    if len(R)%2: R+='0'
    return f'{kind} {k}: {bl(L)} [{"ABCDEFGH"[st]}] {bl(R)}'
if __name__=='__main__':
    n=int(sys.argv[1]); R=sys.argv[2]
    Rs=parse_blocks(R)
    r=run_from('01'*n,Rs)
    print(fmt(r))
