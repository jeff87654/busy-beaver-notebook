import sys
from lit import *
def word(ds,a,b):  # nearest-first ds
    w='0'+'111'+'01'*b+'0'+'01'*a
    for d in ds: w+='0'+'01'*d
    return w+'00000'
if __name__!="__main__": raise SystemExit
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); n=int(sys.argv[4])
w=word(ds,a,b)
s=mk(w,0,'A'); base=s.pos
prev=None
for i in range(n):
    # print when head moves to new minimum position or at state A
    if s.state==0 or s.pos<=base+4:
        print(s.steps, show(s,base-1,base+len(w)))
    if not s.step(): print('HALT'); break
print(s.steps, show(s,base-1,base+len(w)))
