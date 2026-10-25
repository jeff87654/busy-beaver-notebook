import sys
from sim import T
def trace(L,R,st='H',maxn=500,stop='H'):
    tape={}
    for i,c in enumerate(L): tape[i-len(L)]=int(c)
    for i,c in enumerate(R): tape[i]=int(c)
    pos=0; lo=-len(L); hi=len(R)
    for n in range(maxn):
        print('%3d'%n, ''.join((('['+st+']') if p==pos else ' ')+str(tape.get(p,0)) for p in range(lo,hi)))
        s=tape.get(pos,0); tr=T[(st,s)]
        if tr is None: print('HALT'); return
        tape[pos]=tr[0]; pos+=tr[1]; st=tr[2]
        if st==stop and n>0:
            print('%3d'%(n+1), ''.join((('['+st+']') if p==pos else ' ')+str(tape.get(p,0)) for p in range(lo,hi))); return
trace(sys.argv[1],sys.argv[2])
