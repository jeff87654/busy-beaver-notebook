import idle, sys, subprocess, os
HERE=os.path.dirname(os.path.abspath(__file__))
def rruns(s):
    out=[]
    for tok in s.strip().strip('.').split('.'):
        if not tok: continue
        if '^' in tok: c,n=tok.split('^'); out.append((c,int(n)))
        else: out.append((tok,1))
    return out
def pcomp(R):
    # compress repeated windows of length 2 or 4 runs
    o=[];i=0
    while i<len(R):
        best=None
        for w in (2,4,6):
            if i+2*w<=len(R) and R[i:i+w]==R[i+w:i+2*w]:
                k=1
                while i+(k+1)*w<=len(R) and R[i+k*w:i+(k+1)*w]==R[i:i+w]: k+=1
                if k>=3 and (best is None or k*w>best[0]*best[1]): best=(k,w)
        if best:
            k,w=best; o.append('('+''.join('%s%s'%(c,('^%d'%n if n>1 else '')) for c,n in R[i:i+w])+')x%d'%k); i+=k*w
        else:
            c,n=R[i]; o.append('%s%s'%(c,('^%d'%n if n>1 else ''))); i+=1
    return ' '.join(o)
if __name__=='__main__':
    M,N,side,ratio,start=sys.argv[1:6]; ratio=float(ratio); nxt=float(start)
    p=subprocess.Popen([os.path.join(HERE,'ev.exe'),M,N,'1000000000000',side,'1'],stdout=subprocess.PIPE,text=True,creationflags=0x40)
    with open(os.path.join(HERE,'..','pids.txt'),'a') as f: f.write('%d ev.exe\n'%p.pid)
    for l in p.stdout:
        if '|' not in l: print(l.strip(),flush=True); continue
        st=int(l.split()[0])
        if st<nxt: continue
        nxt=st*ratio
        h,r=l.split('|'); print(h.strip(),'|',pcomp(rruns(r))[:400],flush=True)
