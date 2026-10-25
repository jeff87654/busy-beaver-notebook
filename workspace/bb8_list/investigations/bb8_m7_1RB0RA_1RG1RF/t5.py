from evsum import *
from cexp import tw
import sys
c0=int(sys.argv[1]); lim=int(sys.argv[2])
seen=[]
def isK(cfg):
    q,L,Rr,mode=cfg
    if q=='G' and mode=='>' and Rr==[BLANK]:
        seen.append(cfg)
        if len(seen)>=3: return True
    return False
st=('C',[1,1,BLANK],[R('s',Z)]+[1,0,1]*c0+[R('J',Z),0,BLANK],'<')
pl.LEMMAS.clear(); pl.PEELS.clear()
script,c=pl.drive('x',st,None,maxev=600,verbose=False,peel_limit=lim,stop_when=isK)
print(summarize(script))
for cfg in seen: print(cfg[0],cfg[3],'L:',tw(cfg[1])[:300])
