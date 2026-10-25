import sys, re
def rle(w):
    # greedy: try periods 1..8, emit (unit)^k if k>=3
    out=[]; i=0; n=len(w)
    while i<n:
        best=None
        for p in range(1,9):
            u=w[i:i+p]
            if len(u)<p: break
            k=1
            while w[i+k*p:i+(k+1)*p]==u: k+=1
            if k>=3 and (best is None or k*p>best[1]*best[0]): best=(p,k)
        if best:
            p,k=best; out.append('(%s)^%d'%(w[i:i+p],k)); i+=p*k
        else:
            out.append(w[i]); i+=1
    s=' '.join(out)
    return re.sub(r'(?<=[01]) (?=[01](\s|$))','',s)
if __name__=='__main__':
    for line in sys.stdin:
        f=line.split()
        if f and f[0]=='DUMP': print(rle(f[1]), '| head', f[2], f[3])
