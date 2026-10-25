from lit import *
TM_=TM
t=parse(TM);tape={};p=0;q=0
# target: A> 0 11 (01)^2 0^14 U 0^44 U at some position; find first n where head at A on blank-left config with gaps [0,1,1,14,4,1,44,4,1]
def gaps():
    ones=sorted(tape); return [ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
for n in range(5000):
    if q==0 and tape and p<min(tape) and gaps()==[0,1,1,14,4,1,44,4,1] and min(tape)-p==1:
        print("steps",n);break
    w,d,ns=t[(q,tape.get(p,0))]
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
