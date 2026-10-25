from sim import *
import sys,collections,re
N=int(sys.argv[1])
tape={};p=0;q='A';st=0
Ls=collections.Counter();Rs=collections.Counter()
def rl(s):
    return ' '.join(f"{m.group(0)[0]}{len(m.group(0))}" for m in re.finditer(r'0+|1+',s))
while st<N:
    s=tape.get(p,0);t=T[(q,s)]
    if q=='F':
        lo=min(tape);hi=max(tape)
        L=''.join(str(tape.get(i,0)) for i in range(lo,p)).lstrip('0')
        R=''.join(str(tape.get(i,0)) for i in range(p,hi+1)).rstrip('0')
        Ls[L]+=1;Rs[R]+=1
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
print(len(Ls),len(Rs))
import random
for R in sorted(Rs,key=len)[:60]: print('R',R)
for L in sorted(Ls,key=len)[:60]: print('L',L)
print('----')
P=collections.Counter(); G=collections.Counter()
for R,c in Rs.items():
    m=re.match(r'^(.*?)((?:00+1)*)$',R)
    P[m.group(1)]+=c
    gaps=[len(x)-1 for x in re.findall(r'0+1',m.group(2))]
    for i,g in enumerate(gaps): G[(i==0, min(g,9))]+=c
print(P.most_common())
print(sorted(G.items()))
L3=[L for L in Ls if '111' in L]; print('L with 111:',len(L3),L3[:5])
# missing L patterns of length 7
import itertools
allL=set(Ls)
miss=[ '1'+''.join(t) for t in itertools.product('01',repeat=6) if '1'+''.join(t) not in allL]
print('missing len7',miss)
