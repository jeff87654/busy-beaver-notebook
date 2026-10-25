import sys, subprocess, re
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
def D(m): return '10'*m+'1'
def word(toks,r,P=True):
    return ('11' if P else '')+''.join(D(m) for m in toks)+'10'*r+'111001'
def rl(toks):
    out=[];i=0
    while i<len(toks):
        j=i
        while j<len(toks) and toks[j]==toks[i]: j+=1
        out.append(str(toks[i]) if j-i==1 else '%d^%d'%(toks[i],j-i)); i=j
    return '['+','.join(out)+']'
def kseq(toks,r,P=True,N=20000000,maxprint=3,exe='./gk3_s.exe'):
    w=word(toks,r,P)
    args=[exe,M,w,'B',str(N),str(maxprint)]+(['P'] if P else [])
    out=subprocess.run(args,capture_output=True,text=True).stdout
    res=[]
    for line in out.splitlines():
        m=re.match(r'step (\d+) K\[(.*)\] r=(\d+)',line)
        if m:
            res.append((int(m.group(1)),[int(x) for x in m.group(2).split(',')] if m.group(2) else [],int(m.group(3))))
        elif line.startswith('HALT') or line.startswith('EDGE'): res.append(line)
    return res
if __name__=='__main__':
    n0,n1,b0,b1=map(int,sys.argv[1:5]); N=int(sys.argv[5]) if len(sys.argv)>5 else 20000000
    for n in range(n0,n1+1):
        for b in range(b0,b1+1):
            res=kseq([1]*(n+1),3*b+2,True,N,2)
            print('n=%d b=%d'%(n,b), ' ; '.join(('%d %s r=%d'%(r[0],rl(r[1]),r[2]) if isinstance(r,tuple) else r) for r in res) or 'NONE')
