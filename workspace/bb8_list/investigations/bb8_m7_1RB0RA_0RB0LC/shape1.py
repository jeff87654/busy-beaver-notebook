import sys,re
from tr import *
sys.path.insert(0,'../bb8_m7_1RB0RA_1RH1LG')
def kword(n,b,a=0):
    D=lambda m:'10'*m+'1'
    return '11'+D(1)*n+D(3*a+1)+'10'*(3*b+2)+'111001'
pat=re.compile(r'^110110((?:01)*)((?:10)*)11((?:01)*)0011111111001001$')  # after stripping leading zeros
def parse(tp,lo,hi):
    s=''.join(map(str,tp[lo:hi+1])).rstrip('0')
    s=s.lstrip('0')
    m=re.match(r'^11011((?:01)*)((?:10)*)11((?:01)*)00111111110010010?$',s+'0')
    return m
def find(n,b,maxs=20000000):
    w=kword(n,b)
    res=[]
    def show(st,q,p,tp,lo,hi):
        if q==1 and p>=hi and tp[p]==0 and tp[hi]==0:
            s=''.join(map(str,tp[lo:hi+1])).strip('0')
            m=re.match(r'^11011((?:01)*)((?:10)*)11((?:01)*)0011111111001001$',s)
            if m:
                res.append((st,len(m.group(1))//2,len(m.group(2))//2,len(m.group(3))//2))
                raise StopIteration
        return False
    try: run(M,w,len(w),1,maxs,show)
    except StopIteration: pass
    return res
if __name__=='__main__':
    for n in range(0,4):
        for b in range(0,4):
            print(n,b,find(n,b))
