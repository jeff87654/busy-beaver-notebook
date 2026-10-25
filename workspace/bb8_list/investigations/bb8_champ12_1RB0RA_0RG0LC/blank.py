import sys
from fam import *
which=sys.argv[1]; N=int(sys.argv[2])
tm=parse_tm(M1 if which=='1' else M2)
s=Sim(tm,'',q=0,size=1<<22)
cnt=0
while s.steps<N:
    r=s.run(N-s.steps,stop_on=(1,))
    if r in('HALT','EDGE','N'): print(r,s.steps); break
    lw=s.left_word()
    if lw is not None:
        pr=parse_word(lw)
        if pr:
            cnt+=1
            if cnt<=40 or cnt%200==0: print(s.steps,pr if len(str(pr))<200 else (len(pr[0]),pr[0][:6],pr[1],pr[2]))
print('done',s.steps,cnt)
