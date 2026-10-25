from canon import *
import random,re
def s(L): return re.sub('110','T',''.join(map(str,L)))
def Yrun(beta, j, a, G, maxn=10**7):
    L=list(beta)+[1,1,0]*j+[1]; P='111'; GG=[a]+list(G)
    tgt=(list(beta),'11',[2]*(j-1)+[a+5]+list(G))
    for i in range(maxn):
        L,P,GG=step(L,P,GG)
        if len(L)<len(beta) or L[:len(beta)]!=list(beta): return ('touched base',i)
        if (L,P,GG)==tgt: return i+1
    return None
def E1run(beta, j, h, G, maxn=10**7):
    L=list(beta); P='11'; GG=[2]*j+[h]+list(G)
    tgt=(list(beta)+[0],'11',[2]*(j-1)+[h+2]+list(G))
    for i in range(maxn):
        L,P,GG=step(L,P,GG)
        if len(L)<len(beta) or L[:len(beta)]!=list(beta): return ('touched base',i)
        if (L,P,GG)==tgt: return i+1
    return None
bad=0
for t in range(300):
    beta=[random.randint(0,1) for _ in range(random.randint(0,6))]
    j=random.randint(1,6); a=random.randint(0,9); G=[random.randint(2,9) for _ in range(random.randint(0,3))]
    r=Yrun(beta,j,a,G)
    if not isinstance(r,int): print('Y',beta,j,a,G,r); bad+=1
    h=random.randint(4,12)
    r=E1run(beta,j,h,G)
    if not isinstance(r,int): print('E1',beta,j,h,G,r); bad+=1
print('bad',bad)
for j in range(1,8): print(j, Yrun([],j,0,[]), E1run([],j,5,[]))
