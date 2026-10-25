from evsum import *
import sys
c0=int(sys.argv[1]); lim=int(sys.argv[2])
def isK(cfg):
    q,L,Rr,mode=cfg
    if q!='G' or mode!='>' or Rr!=[BLANK]: return False
    suf=[1,0]*7+[1,1,BLANK]
    # L ends with suf
    return L[-len(suf):]==suf and L[:9]==[1,0,1,1,0,1,1,0,1]
st=('C',[1,1,BLANK],[R('s',Z)]+[1,0,1]*c0+[R('J',Z),0,BLANK],'<')
pl.LEMMAS.clear(); pl.PEELS.clear()
script,c=pl.drive('x',st,None,maxev=600,verbose=False,peel_limit=lim,stop_when=isK)
print(summarize(script)); print(cs(c,120)); print(dict(pl.PEELS))
