import sys
from collections import Counter
m=sys.argv[1]; N=int(sys.argv[2])
T={}
for i,s in enumerate(m.split('_')):
    for c in (0,1):
        t=s[3*c:3*c+3]
        T[(i,c)]=None if t[0]=='-' else (int(t[0]),1 if t[1]=='R' else -1,ord(t[2])-65)
tape=bytearray(2*N+10); pos=N+5; q=0; cnt=Counter(); first={}
for st in range(N):
    c=tape[pos]; t=T[(q,c)]
    k=chr(65+q)+str(c); cnt[k]+=1
    if k not in first: first[k]=st
    if t is None: print('HALT',st); break
    tape[pos]=t[0]; pos+=t[1]; q=t[2]
print(sorted(cnt.items())); print({k:v for k,v in first.items()})
