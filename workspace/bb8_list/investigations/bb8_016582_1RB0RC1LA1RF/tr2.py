from lit import *
import re,sys
t=parse(TM);tape={};p=0;q=0
def rle(s): return " ".join(f"{m.group(0)[0]}^{len(m.group(0))}" if len(m.group(0))>1 else m.group(0)[0] for m in re.finditer(r"0+|1+",s))
lo=0;cnt=0;N=int(sys.argv[1])
for n in range(N):
    r=t[(q,tape.get(p,0))]
    if r is None: print("halt",n);break
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
    if p<lo:
        lo=p
        if q==0:
            cnt+=1
            print(n,p,rle(render(tape,p,q)))
