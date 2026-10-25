import idle, random, sys
from rules import nextk
from sim import M1, M2
def predict(a,ds,w):
    if ds and ds[0]>0:
        st=12*a*a+66*a+(56 if w==1 else 58)
        return ('K',st,(3*a+3,[ds[0]-1]+ds[1:]))
    k=0
    while k<len(ds) and ds[k]==0: k+=1
    if k>3*a: return ('BAD',)
    if k==len(ds):
        st=48*a*a+(192 if w==1 else 198)*a+(137-28*k if w==1 else 143-30*k)
        return ('HALT',st,6*a+7)
    st=12*a*a+(24*k+66)*a+74+10*(k-1)-4*(k-1)*(k-2)+(0 if w==1 else 2*(k+1))
    return ('K',st,(1,[1]*(k-1)+[3*a+3-k,ds[k]-1]+ds[k+1:]))
random.seed(int(sys.argv[1]))
N=int(sys.argv[2]); bad=0; cnt={'K':0,'HALT':0}
for it in range(N):
    w=random.choice((1,2)); M=M1 if w==1 else M2
    n=random.randint(1,22)
    kind=random.random()
    if kind<0.4: ds=[random.choice((0,0,1,2,random.randint(0,50),random.randint(0,3000))) for _ in range(n)]
    elif kind<0.7: k=random.randint(1,n); ds=[0]*k+[random.randint(0,40) for _ in range(n-k)]
    else: ds=[0]*n
    k=0
    while k<len(ds) and ds[k]==0: k+=1
    a=random.choice((max(1,(k+2)//3), max(1,(k+2)//3)+1, random.randint(max(1,(k+2)//3),50), random.randint(max(1,(k+2)//3),3000)))
    p=predict(a,ds,w); r=nextk(M,a,ds,maxs=10**12)
    if p[0]=='K': ok = r[0]=='K' and r[1]==p[1] and tuple(r[2])==p[2]
    else: ok = r[0]=='HALT' and r[1]==p[1] and r[2]==p[2] and r[3].s==2 and r[3].h==1
    cnt[p[0]]+=1
    if not ok:
        bad+=1; print('MISMATCH',w,a,ds,p,r[:3])
print('tests',N,cnt,'bad',bad)
# boundary k=3a+1 should NOT behave as rule
fails=0
for a in range(1,7):
    k=3*a+1; r=nextk(M1,a,[0]*k+[1],maxs=3*10**6); r2=nextk(M1,a,[0]*k,maxs=3*10**6)
    print('k=3a+1 a=',a,'B result',r[0],'E result',r2[0])
