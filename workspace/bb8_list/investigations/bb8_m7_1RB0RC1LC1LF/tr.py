import sys
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
ST='ABCDEFGH'
tm={}
for i,row in enumerate(M.split('_')):
    for c in range(2):
        x=row[3*c:3*c+3]
        tm[(i,c)]=None if x=='---' else (int(x[0]),1 if x[1]=='R' else -1,ST.index(x[2]))
def word(ds,a,b):
    P='1001';u='010';s='001'
    x=P
    for d in ds: x+=u*d+s
    x+=u*a+s+u*b
    return x
def start(ds,a,b):
    w=word(ds,a,b)[::-1]
    tape={i:1 for i,c in enumerate(w) if c=='1'}
    return tape,-1,6   # head left of word in G
def show(tape,pos,q,lo=None,hi=None):
    if lo is None: lo=min(min(tape),pos)-1
    if hi is None: hi=max(max(tape),pos)+1
    return ''.join(('['+ST[q].lower()+']' if i==pos and False else '')+str(tape.get(i,0)) for i in range(lo,hi+1)), lo
def run(tape,pos,q,n,verbose=True,every=1):
    lo0=min(tape)-8 if tape else -8
    for step in range(1,n+1):
        s=tape.get(pos,0)
        tr=tm[(q,s)]
        if tr is None:
            print('HALT',step,ST[q],s);return tape,pos,q,step
        w,d,nq=tr
        if w: tape[pos]=1
        else: tape.pop(pos,None)
        pos+=d;q=nq
        if verbose and step%every==0:
            hi=max(max(tape),pos)+4
            line=''.join((ST[q].lower()+str(tape.get(i,0)) if i==pos else str(tape.get(i,0))) for i in range(lo0,hi))
            print('%4d %s'%(step,line))
    return tape,pos,q,n
if __name__=='__main__':
    ds=eval(sys.argv[1]);a=int(sys.argv[2]);b=int(sys.argv[3]);n=int(sys.argv[4])
    t,p,q=start(ds,a,b)
    run(t,p,q,n)
