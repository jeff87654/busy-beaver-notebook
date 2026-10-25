import subprocess, sys
M='1RB0RA_1LC1LF_1RD0LB_1RA1LE_1RA0LC_1RG1LE_0RH0RF_---0RF'
# literal blank-start simulation for 2117 steps, compare with K(2,0^10;0;0) word
T={}
for i,part in enumerate(M.split('_')):
    for s in range(2):
        tr=part[3*s:3*s+3]
        T[(chr(65+i),s)]=None if tr=='---' else (int(tr[0]),1 if tr[1]=='R' else -1,tr[2])
tape={};p=0;q='A'
for st in range(1,3000):
    r=T[(q,tape.get(p,0))]
    if r is None: print('halt',st);break
    tape[p]=r[0];p+=r[1];q=r[2]
    if st==2117: break
lo=min(k for k,v in tape.items() if v);hi=max(k for k,v in tape.items() if v)
left=''.join(str(tape.get(i,0)) for i in range(lo,p))
print('state',q,'head',p,'hi',hi,'steps',st)
def D(m): return '10'*m+'1'
def word(ds,a,b):
    w='11'
    for d in ds: w+=D(3*d+1)
    w+=D(3*a+1)+'10'*(3*b+2)+'111001'
    return w
w=word([2]+[0]*10,0,0)
print(left==w, len(left), len(w))
open('first_word.txt','w').write(w)
