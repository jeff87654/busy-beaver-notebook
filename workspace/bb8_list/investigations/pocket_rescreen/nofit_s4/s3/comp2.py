# comp2.py: generic compressor helpers + event view: comp2.py M N Q side every
import sys,subprocess,re
sys.path.insert(0,r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen')
import idle
from val import expand
def comp(t,maxp=60):
    o=[];i=0;n=len(t)
    while i<n:
        best=(0,0,0)
        for p in range(1,maxp+1):
            if i+2*p>n: break
            k=1
            while t[i+k*p:i+(k+1)*p]==t[i:i+p]: k+=1
            if k>=2 and k*p>=max(6,2*p) and k*p>best[0]: best=(k*p,p,k)
        if best[0]:
            u=t[i:i+best[1]]; o.append(('%s^%d' if best[1]==1 else '(%s)^%d')%(u,best[2])); i+=best[0]
        else:
            if o and re.fullmatch('[01]+',o[-1]): o[-1]+=t[i]
            else: o.append(t[i])
            i+=1
    return ' '.join(o)
if __name__=='__main__':
    M,N,Q,S,ev=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],int(sys.argv[5])
    p=subprocess.Popen([r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\pocket_rescreen\nofit_s4\s3\sim.exe',M,N,'at',Q,S,'100000000'],stdout=subprocess.PIPE,text=True)
    c=0
    for ln in p.stdout:
        m=re.match(r'(\d+) (\w) \| (.*) <\w> (.*)$',ln.strip())
        if not m: print(ln.strip()); continue
        c+=1
        if c%ev: continue
        print(m.group(1),comp(expand(m.group(3)))+' | '+comp(expand(m.group(4))))
