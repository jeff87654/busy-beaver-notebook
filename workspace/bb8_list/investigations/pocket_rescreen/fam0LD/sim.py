import sys
def parse(m):
    T={}
    for i,r in enumerate(m.split('_')):
        for c in (0,1):
            t=r[3*c:3*c+3]
            if t[2] in '-Z': continue
            T[(i,c)]=(int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
    return T
def rle(s):
    out=[];i=0
    while i<len(s):
        j=i
        while j<len(s) and s[j]==s[i]: j+=1
        out.append(s[i]+('^%d'%(j-i) if j-i>2 else s[i]*(j-i-1)) ); i=j
    return ''.join(out)
def run(m,steps,tape=None,pos=0,st=0,show=True):
    T=parse(m); tape=dict(tape or {}); 
    for n in range(steps):
        c=tape.get(pos,0)
        if (st,c) not in T: return ('H',n,tape,pos,st)
        w,d,q=T[(st,c)]; tape[pos]=w; pos+=d; st=q
        if show and st==6 and tape.get(pos,0)==0:
            ks=[k for k,v in tape.items() if v]
            if not ks or min(ks)>pos:
                hi=max(ks) if ks else pos
                print(n+1, rle(''.join(str(tape.get(i,0)) for i in range(pos+1,hi+1))))
    return ('T',steps,tape,pos,st)
if __name__=='__main__':
    run(sys.argv[1],int(sys.argv[2]))
