import sys,re
# input: lines from snapf (RLE tokens) -> rebuild bit string -> compress periodic blocks (period 1..8, >=4 reps)
for line in sys.stdin:
    if '|' not in line: print(line.strip()); continue
    head,body=line.split('|',1)
    bits=''.join(t[0]*(int(t[2:]) if '^' in t else 1) for t in body.split())
    out=[];i=0;n=len(bits)
    while i<n:
        best=None
        for p in range(1,9):
            u=bits[i:i+p]
            if len(u)<p: break
            k=1
            while bits[i+k*p:i+(k+1)*p]==u: k+=1
            if k>=4 and (best is None or k*p>best[1]*best[0]): best=(p,k)
        if best: p,k=best; out.append('(%s)^%d'%(bits[i:i+p],k)); i+=p*k
        else:
            j=i
            while j<n and j<i+1: j+=1
            out.append(bits[i:j]); i=j
    s=' '.join(out); s=re.sub(r'(?<=[01]) (?=[01](?: |$))','',s)
    print(head.strip(),'|',s[:700])
