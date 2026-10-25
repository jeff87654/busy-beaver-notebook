import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF"
pl.set_tm(TM)
U=[1,0,0,0,0,1,0,1]
M={'m':1}; A_={'a':1}; D_={'d':1}
def X(pre, mcnt, mconst, a_cnt, r):
    """A> 0 11 [010101]^m (01)^mconst  0^a  U r"""
    return ('A',[BLANK],[0,1,1]+mkrun((0,1,0,1,0,1),mcnt)+[0,1]*mconst+mkrun((0,),a_cnt)+U+r,'>')
R=[V('r')]
PH={}
# N1: X(m, a+2, r) -> X(m+1, a+1, r);  j=3m+2 : (01)^2 extra
def X2(mcnt,mc,acnt,acst,r):
    # 3m'+2 : m' variable count mcnt (dict), plus mc const
    return X(None,mcnt,2,acnt,r)
PH['N1']=(('A',[BLANK],[0,1,1]+mkrun((0,1,0,1,0,1),M)+[0,1,0,1]+mkrun((0,),A_,2)+U+R,'>'),
          ('A',[BLANK],[0,1,1]+mkrun((0,1,0,1,0,1),{'m':1})+[0,1,0,1,0,1,0,1,0,1]+mkrun((0,),A_,1)+U+R,'>'))
if __name__=='__main__':
    for w in sys.argv[1:]:
        s,t=PH[w]
        drive(w,s,t,matchers=(),maxev=300,verbose=True)
