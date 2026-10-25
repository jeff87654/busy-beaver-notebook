from xg import *
import sys
def word0(n,b):  # K0 used-up list, champion tail
    return wordx([1]*(n+1),3*b+2,True,'111001')
def seq(n,b,N=200000000,maxprint=100000,skip=0,tail='0111001'):
    w=word0(n,b)
    out=subprocess.run(['./gk5.exe',M,w,'B',str(N),str(maxprint),tail,'1',str(skip)],capture_output=True,text=True).stdout.strip().split('\n')
    res=[]
    for l in out:
        if l.startswith('step'):
            st=int(l.split()[1]); body=l[l.index('[')+1:l.index(']')]
            toks2=[int(x) for x in body.split(',')] if body else []
            r2=int(l.split('r=')[1].split()[0])
            res.append((st,toks2,r2))
        elif l.startswith('HALT') or l.startswith('EDGE') or l.startswith('done'): res.append(l)
    return res
def rl(toks):
    out=[];i=0
    while i<len(toks):
        j=i
        while j<len(toks) and toks[j]==toks[i]: j+=1
        out.append(str(toks[i]) if j-i==1 else '%d^%d'%(toks[i],j-i)); i=j
    return '['+','.join(out)+']'
if __name__=='__main__':
    n,b,N=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
    s=seq(n,b,N)
    prev=None
    for x in s:
        if isinstance(x,str): print(x); continue
        st,t,r=x
        if prev is not None:
            pt,pr=prev
            if len(pt)==len(t) and pt[:-1]==t[:-1] and pt[-1]-1==t[-1] and r==pr+2: prev=(t,r); continue
        print(st,rl(t),r)
        prev=(t,r)
