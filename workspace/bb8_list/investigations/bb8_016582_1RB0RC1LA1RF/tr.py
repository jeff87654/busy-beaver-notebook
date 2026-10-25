from lit import *
import re
t=parse(TM);tape={};p=0;q=0
def rle(s): return " ".join(f"{m.group(0)[0]}^{len(m.group(0))}" if len(m.group(0))>1 else m.group(0)[0] for m in re.finditer(r"0+|1+",s))
lo=0;cnt=0
for n in range(200000):
    r=t[(q,tape.get(p,0))]
    if r is None: print("halt",n);break
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
    if p<lo-0 and q==0 or (p<lo):
        lo=p
        # new leftmost
        s=render(tape,p,q)
        cnt+=1
        if cnt<60: print(n,rle(s))
