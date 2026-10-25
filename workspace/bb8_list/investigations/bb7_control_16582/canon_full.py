import re,sys
tok=re.compile(r'(\d{3})\^(\(~ [^)]*\)|\d+)')
CAP=5000
def expand(part):
    bl=tok.findall(part)
    s=''
    for b,e in bl:
        n = CAP if (e.startswith('(') or int(e)>=CAP) else int(e)
        s+=b*n
    return s
def canon(bits,headpos,state):
    out=[];i=0
    while i<len(bits):
        if i==headpos:
            out.append('['+state+bits[i]+']'); i+=1; continue
        best=None
        for u,name in (('100','S'),('110','D')):
            k=0
            while bits.startswith(u,i+3*k) and not (i<=headpos<i+3*(k+1)): k+=1
            if k>=2 and (best is None or k>best[1]): best=(name,k)
        if best:
            n=best[1]
            out.append(f'{best[0]}{n if n<CAP-10 else "X"}'); i+=3*n
        else:
            out.append(bits[i]); i+=1
    s=' '.join(out)
    s=re.sub(r'(?<![SDX0-9\]])((?:[01] )+[01])(?![0-9\[])', lambda m: m.group(1).replace(' ',''), s)
    return s
for ln in sys.stdin:
    m=re.match(r'^ +(\d+)  000\^inf (.*?) 000\^inf',ln)
    if not m: continue
    loop,body=m.groups()
    h=re.search(r'\((\d{3})\) ([A-G])>|<([A-G]) \((\d{3})\)',body)
    if not h: continue
    L=body[:h.start()]; R=body[h.end():]
    if h.group(1):
        bits=expand(L)+h.group(1); hp=len(bits); bits+=expand(R); st=h.group(2)
    else:
        bits=expand(L); hp=len(bits)-1; bits+=h.group(4)+expand(R); st=h.group(3)
    bits='000'+bits+'000'; hp+=3
    # trim leading zeros but keep head
    lead=len(bits)-len(bits.lstrip('0')); lead=min(lead,hp); lead=max(0,lead-1)
    bits=bits[lead:]; hp-=lead
    bits=bits.rstrip('0')+'0'
    if hp>=len(bits): bits+= '0'*(hp-len(bits)+1)
    print(loop, canon(bits,hp,st))
