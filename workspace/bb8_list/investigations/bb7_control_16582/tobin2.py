import re,sys
tok=re.compile(r'(\d{3})\^(\(~ [^)]*\)|\d+)')
CAP=5000
def canon(bits):
    out=[];i=0
    while i<len(bits):
        best=None
        for u,name in (('100','S'),('110','D')):
            k=0
            while bits.startswith(u,i+3*k): k+=1
            if k>=2 and (best is None or k>best[1]): best=(name,k)
        if best:
            n=best[1]
            out.append(f'{best[0]}{n if n<CAP-10 else "X"+str(n-CAP)}'); i+=3*best[1]
        else:
            out.append(bits[i]); i+=1
    s=' '.join(out)
    # glue literal bits
    s=re.sub(r'(?<![SDX0-9-])((?:[01] )+[01])(?![0-9])', lambda m: m.group(1).replace(' ',''), s)
    return s
for ln in sys.stdin:
    m=re.match(r'^ +(\d+)  000\^inf (<[A-G]) \((\d{3})\) (.*?) 000\^inf',ln)
    if not m: continue
    loop,st,bs,rest=m.groups()
    blocks=tok.findall(rest)
    exps=[(b,(CAP if (e.startswith('(') or int(e)>=CAP) else int(e))) for b,e in blocks]
    bits=bs+''.join(b*e for b,e in exps)
    print(loop, st[1]+'0 |', canon(bits))
