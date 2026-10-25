from lit import parse, render
TMS="1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_1RB1LE_---1LF"
t=parse(TMS);tape={};p=0;q=0
for n in range(300):
    if n in (239,257,275,293):
        print(n, render(tape,p,q))
    w,d,ns=t[(q,tape.get(p,0))]
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
