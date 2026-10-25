import idle
from rules import *
cfgs=[([],B) for B in range(0,1201)]
res=literal(X,cfgs,10**9)
bad=0; st=[]
for (ds,B),r in zip(cfgs,res):
    pr=predict(ds,B)
    ok = (pr[0]==r[0]) and ((pr[0]=='HALT' and pr[1]==r[1]) or (pr[0]=='K' and pr[1]==r[1] and pr[2]==r[2]))
    if not ok: bad+=1; print('MISS',B,pr,r[:3])
    st.append((B,r[0],r[-1]))
print('E bad',bad)
print([s for s in st[:12]])
# fit steps: odd halts, even rebuild
import numpy as np
for par in (0,1):
    xs=[s[0] for s in st if s[0]%2==par and s[0]>=2]; ys=[s[2] for s in st if s[0]%2==par and s[0]>=2]
    c=np.polyfit(xs,ys,2); print('parity',par,'fit',c, 'maxerr', max(abs(np.polyval(c,x)-y) for x,y in zip(xs,ys)))
