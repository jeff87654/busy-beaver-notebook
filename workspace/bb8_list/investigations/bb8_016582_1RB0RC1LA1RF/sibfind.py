from lit import parse, render
TMS="1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_1RB1LE_---1LF"
t=parse(TMS);tape={};p=0;q=0
import re
for n in range(400):
    s=render(tape,p,q) if tape else ""
    m=re.fullmatch(r"\[E\]0101((0001)*)",s)
    if m:
        print(n, len(m.group(1))//4); 
        if n>100: break
    w,d,ns=t[(q,tape.get(p,0))]
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
