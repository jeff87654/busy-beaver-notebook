import sys,re
# second-level compression of sim.exe output lines: tokens = run tokens or single chars
def tok(s):
    return re.findall(r'\([01]+\)\^\d+|[01]\^\d+|[01]|<[A-H]>|\|',s)
def comp(t):
    out=[];i=0;n=len(t)
    while i<n:
        best=(0,0,0)
        for p in range(1,13):
            k=1
            while i+(k+1)*p<=n and t[i+k*p:i+(k+1)*p]==t[i:i+p]: k+=1
            if k>=2 and k*p>best[0] and (k>=3 or p>1) : best=(k*p,p,k)
        if best[0]>=4:
            p,k=best[1],best[2]; out.append('['+' '.join(t[i:i+p])+']^'+str(k)); i+=k*p
        else: out.append(t[i]); i+=1
    return out
def merge(t):
    # merge adjacent single chars into strings
    o=[];buf=''
    for x in t:
        if re.fullmatch('[01]',x): buf+=x
        else:
            if buf:o.append(buf);buf=''
            o.append(x)
    if buf:o.append(buf)
    return o
for line in sys.stdin:
    parts=line.split(None,2)
    if len(parts)<3: print(line.rstrip()); continue
    t=merge(tok(parts[2]))
    print(parts[0],parts[1],' '.join(comp(t))[:int(sys.argv[1]) if len(sys.argv)>1 else 300])
