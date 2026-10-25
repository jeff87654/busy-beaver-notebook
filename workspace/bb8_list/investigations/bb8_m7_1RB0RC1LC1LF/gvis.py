import sys
from tr import tm, ST, word
def blocks(s):
    # parse tape string (from head cell) into U/S blocks if possible
    out=[];i=0
    s=s.rstrip('0')
    # consume from index 1 (after head cell)
    while i<len(s):
        t=s[i:i+3]
        if t=='010': out.append('U')
        elif t=='100': out.append('S')
        elif t=='1': out.append('1')
        elif len(t)<3 and set(t)<=set('01'):
            out.append('<'+t+'>')
        else: out.append('['+t+']')
        i+=3
    return ' '.join(out)
def runv(ds,a,b,maxsteps=2000000,maxvis=60):
    w=word(ds,a,b)[::-1]
    tape={i:1 for i,c in enumerate(w) if c=='1'}
    pos=-1;q=6
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
        if q==6 and pos<min(tape):
            # head left of everything: G visit at left end
            hi=max(tape)
            s_=''.join(str(tape.get(i,0)) for i in range(pos,hi+1))
            # head cell is s_[0]; word begins at s_[1]
            print(step, blocks(s_[1:]))
            vis+=1
            if vis>=maxvis: return
if __name__=='__main__':
    ds=eval(sys.argv[1]);a=int(sys.argv[2]);b=int(sys.argv[3])
    runv(ds,a,b)
