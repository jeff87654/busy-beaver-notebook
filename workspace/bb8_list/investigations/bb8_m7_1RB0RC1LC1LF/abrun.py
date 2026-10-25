import sys
from tr import tm, ST
from absys import toks
def abs_next(w):
    # w: list of tokens (strings 'U','S','V'); returns new list or None (stuck)
    n=len(w)
    i=0
    while i<n and w[i]=='U': i+=1
    if i==0: return None
    k=0
    while i+k<n and w[i+k]=='S': k+=1
    if k==0: return None
    ii=i
    if i+k==n:
        # end of tape
        if ii>=3: return ['U']*(ii-2)+['S']+['V']*(k+1)+['S']
        if ii==2: return ['U']*2+['S']+['V']*k+['S']
        return None
    T=w[i+k]
    rest=w[i+k+1:]
    if T=='U':
        return ['U']+['S']*(ii-1)+['U']*(k-1)+['S','V']+rest
    if T=='V':
        return ['U']+['S']*(ii-1)+['U']*k+['S']+rest
    return None
def blank_visits(maxvis):
    tape={};pos=0;q=0
    out=[]
    step=0
    while len(out)<maxvis:
        step+=1
        v=tape.get(pos,0)
        tr=tm[(q,v)]
        if tr is None:
            out.append((step,'HALT'));break
        w_,d,q=tr
        if w_: tape[pos]=1
        else: tape.pop(pos,None)
        pos+=d
        if q==6 and tape and pos<min(tape):
            hi=max(tape)
            ss=''.join(str(tape.get(i,0)) for i in range(pos+1,hi+1))
            out.append((step,toks(ss)))
        if step>200000000: break
    return out
if __name__=='__main__':
    vis=blank_visits(int(sys.argv[1]))
    # find first visit that is a token string
    print(vis[:3])
    w=None
    cnt=0;bad=0
    # align: use first visit with all tokens in USV
    for idx,(st,t) in enumerate(vis):
        if t=='HALT': print('machine halts at',st);break
        if not all(x in 'USV' for x in t): 
            print('non-token visit',idx,st,''.join(t)); continue
        if w is None:
            w=t; print('start abstract at visit',idx,st,''.join(t)); continue
        w=abs_next(w)
        if w is None: print('abstract stuck at',idx);break
        cnt+=1
        if w!=t:
            bad+=1; print('MISMATCH at',idx,st,''.join(w)[:60],'vs',''.join(t)[:60]);break
    print('checked',cnt,'bad',bad)
