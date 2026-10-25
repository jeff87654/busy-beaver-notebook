import sys
sys.path.insert(0,'.')
from kcls import parse
M=sys.argv[1]; word=sys.argv[2]; head=int(sys.argv[3]); N=int(sys.argv[4]); every=int(sys.argv[5])
t=parse(M); L=1<<16; off=L//2; tape=bytearray(L); tape[off:off+len(word)]=bytes(int(c) for c in word); h=off+head; q=4
for n in range(N):
    if n%every==0:
        nz=[i for i in range(L) if tape[i]] or [h]
        lo=min(nz+[h]); hi=max(nz+[h])
        s=''.join(('['+chr(65+q)+']' if i==h else '')+str(tape[i]) for i in range(lo,hi+1))
        print(n, s if len(s)<220 else s[:110]+'...'+s[-100:])
    c=tape[h]; tr=t[2*q+c]
    if tr is None: print('HALT',n); break
    tape[h]=tr[0]; h+=tr[1]; q=tr[2]
