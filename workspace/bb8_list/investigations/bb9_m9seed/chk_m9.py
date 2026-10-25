from tm import *
from collections import Counter
M9='1RB1RA_0LI1RC_0LD1LG_0RE1LD_1RF1RF_0RB0RA_1RA0LH_1LG1LH_---0LD'
tm,n=parse(M9)
u=Counter()
r=run(tm,usage=u); print('blank',r[0],r[1],sum(r[2].values()))
for Z in (1,):
    tape=[0,0]+[1,1,1,1,0,0]*Z
    u=Counter(); r=run(tm,tape=tape,pos=0,q=0,maxs=10**8,usage=u)
    print('Z',Z,r[0],r[1],'ones',sum(r[2].values()))
    print(sorted((chr(65+k[0])+str(k[1]),v) for k,v in u.items()))
