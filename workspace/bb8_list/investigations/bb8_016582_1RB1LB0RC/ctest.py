from canon import *
import random
def Crun(beta, m, h, G, maxn=10**7):
    L=list(beta)+[1,1,0]; P='11'; GG=[2]*m+[h]+list(G)
    tgt=(list(beta),'11',[2]*(m+1)+[h]+list(G))
    for i in range(maxn):
        try: L,P,GG=step(L,P,GG)
        except Stuck as e: return ('stuck',str(e),i)
        if len(L)<len(beta) or L[:len(beta)]!=list(beta): return ('touched base',i)
        if (L,P,GG)==tgt: return i+1
    return None
bad=0
for m in range(0,6):
    for h in range(4,14):
        beta=[random.randint(0,1) for _ in range(random.randint(0,5))]
        G=[random.randint(2,9) for _ in range(random.randint(0,3))]
        r=Crun(beta,m,h,G)
        if not isinstance(r,int): print('C fail',m,h,beta,G,r); bad+=1
print('bad',bad)
print([Crun([],m,5,[]) for m in range(6)])
