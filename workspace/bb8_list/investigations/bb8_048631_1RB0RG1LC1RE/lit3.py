import sys
from lit import *
def word(ds,a,b):
    w='0'+'111'+'01'*b+'0'+'01'*a
    for d in ds: w+='0'+'01'*d
    return w+'0000000'
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); n=int(sys.argv[4])
w=word(ds,a,b)
s=mk(w,0,'A'); base=s.pos
last=-1
for i in range(n):
    if s.state==0:
        t=''.join(str(s.tape[j]) for j in range(base-1,base+len(w)+2))
        p=s.pos-(base-1)
        print('%5d L=%s A R=%s'%(s.steps, t[:p].lstrip('0'), t[p:].rstrip('0')))
    if not s.step(): print('HALT'); break
