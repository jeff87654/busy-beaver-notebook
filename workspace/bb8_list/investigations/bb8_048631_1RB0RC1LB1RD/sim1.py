import sys
M="1RB---_0RC1LG_1LB1RD_0RE1RA_1RF0LC_1LE1RG_0LH1RE_0RB1LG"
T={}
for qi,part in enumerate(M.split('_')):
    for s in (0,1):
        t=part[3*s:3*s+3]
        T[(qi,s)]=None if t=='---' else (int(t[0]),t[1],ord(t[2])-65)
def run(n,show=()):
    tape={};pos=0;q=0
    hist=[]
    for step in range(n):
        s=tape.get(pos,0)
        t=T[(q,s)]
        if t is None:
            return ('halt',step,tape,pos,q)
        w,d,nq=t
        tape[pos]=w
        pos+=1 if d=='R' else -1
        q=nq
    return ('run',n,tape,pos,q)
if __name__=='__main__':
    n=int(sys.argv[1])
    r=run(n)
    print(r[0],r[1],'pos',r[3],'state','ABCDEFGH'[r[4]])
    ks=[k for k,v in r[2].items() if v]
    print(len(ks),min(ks),max(ks))
    lo=min(min(ks),r[3]);hi=max(max(ks),r[3])
    print(''.join(str(r[2].get(i,0)) for i in range(lo,hi+1)),lo)
