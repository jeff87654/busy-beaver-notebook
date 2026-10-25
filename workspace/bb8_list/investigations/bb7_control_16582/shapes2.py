import re,sys
lines=open(sys.argv[1]).read().splitlines()
prevshape=None
tok=re.compile(r'(\d{3})\^(\(~ [^)]*\)|\d+)')
for ln in lines:
    m=re.match(r'^ +(\d+)  000\^inf (<[A-G] \(\d{3}\)) (.*) 000\^inf',ln)
    if not m: continue
    loop,head,rest=m.groups()
    blocks=tok.findall(rest)
    def ab(e):
        if e.startswith('('): return 'BIG'+e[2:-1].replace(' ','')
        if len(e)>6: return 'B%de%d'%(int(e[:2]),len(e)-1)
        return e
    shape=head+' '+' '.join(b for b,e in blocks)
    s=head+' '+' '.join(b+'^'+ab(e) for b,e in blocks)
    print(loop,s)
