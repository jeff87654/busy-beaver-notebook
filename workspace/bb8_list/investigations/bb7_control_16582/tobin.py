import re,sys
tok=re.compile(r'(\d{3})\^(\d+)')
def tobin(cfg):
    # cfg like "<D (100) 100^5 101^1 ..." (right part only, head at left edge)
    m=re.match(r'\s*(<[A-G]|[A-G]>)?\s*\((\d{3})\)\s*([A-G]>)?(.*)',cfg)
    return m
def canon(bits):
    # tokenize: runs of 100 (S) and 110 (D) with >=2 reps; else literal
    out=[];i=0
    while i<len(bits):
        best=None
        for u,name in (('100','S'),('110','D')):
            k=0
            while bits.startswith(u,i+3*k): k+=1
            if k>=2 and (best is None or k>best[1]): best=(name,k)
        if best:
            out.append(f'{best[0]}{best[1]}'); i+=3*best[1]
        else:
            out.append(bits[i]); i+=1
    return ' '.join(out)
for ln in sys.stdin:
    m=re.match(r'^ +(\d+)  000\^inf (<[A-G]) \((\d{3})\) (.*?) 000\^inf',ln)
    if not m: continue
    loop,st,bs,rest=m.groups()
    blocks=tok.findall(rest)
    if any(int(e)>3000 for b,e in blocks): continue
    if '(~' in rest: continue
    # head at rightmost cell of the blank block to the left, state st[1]
    bits=bs+''.join(b*int(e) for b,e in blocks)
    print(loop, st[1]+'0 |', canon(bits))
