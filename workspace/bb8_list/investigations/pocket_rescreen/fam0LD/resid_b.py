# M_b single-digit map: c%3==1 halt; c=3k -> (46*4^k-13)/3 ; c=3k+2 -> (58*4^k-13)/3   (k=c//3)
import math
def F(c,R):   # c known mod 3^(R+1) (or exact if R None); returns c' mod 3^R
    k=c//3 if c%3==0 else (c-2)//3
    A=46 if c%3==0 else 58
    mod=3**(R+1)
    return ((A*pow(4,k,mod)-13)%mod)//3
c=3; seq=[3]
while c<10**6 and c%3!=1:
    k=c//3 if c%3==0 else (c-2)//3; A=46 if c%3==0 else 58
    c=(A*4**k-13)//3; seq.append(c)
print('exact singles:',[s if s<10**15 else '~%.4e'%s for s in seq],'mods',[s%3 for s in seq])
# continue with residues
R=400; cm=c% 3**(R+1)
for r in range(1,60):
    if cm%3==1: print('round',r,'HALT class (c=1 mod 3) -> halts'); break
    cm=F(cm,R); R-=1
    print('round',r,'next c mod 3 =',cm%3,' (precision 3^%d)'%R)
# size: log2 of successive singles: c' ~ A/3 * 4^(c/3) -> log2 c' ~ 2c/3
