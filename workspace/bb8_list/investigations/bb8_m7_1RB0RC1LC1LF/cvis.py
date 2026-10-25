import sys
from tr import tm, ST, word
def runc(ds,a,b,st_letter='C',maxsteps=400000,maxvis=40):
    w=word(ds,a,b)[::-1]
    tape={i:1 for i,c in enumerate(w) if c=='1'}
    pos=-1;q=6
    qq=ST.index(st_letter)
    vis=0
    for step in range(1,maxsteps+1):
        s=tape.get(pos,0)
        tr=tm[(q,s)]
        if tr is None:
            print('HALT at',step);return
        w_,d,q=tr
        if w_: tape[pos]=1
        else: tape.pop(pos,None)
        pos+=d
        if q==qq and pos<=min(tape)+1:
            lo=min(tape)-2
            hi=max(tape)
            s_=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
            print(step, 'pos',pos-lo, s_)
            vis+=1
            if vis>=maxvis: return
if __name__=='__main__':
    ds=eval(sys.argv[1]);a=int(sys.argv[2]);b=int(sys.argv[3])
    runc(ds,a,b,sys.argv[4] if len(sys.argv)>4 else 'C')
