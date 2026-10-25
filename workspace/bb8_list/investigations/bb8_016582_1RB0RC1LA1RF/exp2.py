import threading,os
threading.Timer(40, lambda: os._exit(3)).start()
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show
TM = "1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF"
pl.set_tm(TM)
U=[1,0,0,0,0,1,0,1]
def Z(name):
    return {name:1}
def W(mcnt, extra01, acnt, r):
    """A> 0 11 [010101]^mcnt (01)^extra01  0^acnt(dict,const) U r"""
    return ('A',[BLANK],[0,1,1]+mkrun((0,1,0,1,0,1),mcnt)+[0,1]*extra01+mkrun((0,),acnt[0],acnt[1])+U+r,'>')
def digit(dcnt):  # 0^d U 0^inf , dcnt=(dict,const)
    return mkrun((0,),dcnt[0],dcnt[1])+U+[BLANK]
R=[V('r')]; NIL=[BLANK]
m={'m':1}; a={'a':1}; none={}
PH={}
# N1
PH['N1']=(W(m,2,(a,2),R), W(m,5,(a,1),R))
# N2: X(m,1,0^{d+5}) -> Y(m+7, d+1)
PH['N2']=(W(m,2,(none,1),digit((a,5))), W(m,1+7*3,(a,1),NIL))   # placeholder; Y(m+7,..) = m blocks + 7 blocks(=21 pairs) + 01
# N3: Y(m+1,a+5,nil) -> X(0, 6(m+1)-1 = 6m+5, 0^{a+1} U 0^inf)
PH['N3']=(W(m,1,(a,5),NIL), W({},2,({'m':6},5),digit((a,1))))
PH['N2p']=(W(m,2,(none,1),digit((none,4))), W({},1,({'m':6},53),NIL))
PH['N3p']=(W({},1,(a,13),NIL), W({},2,(none,14),digit((a,1))))
PH['C1']=(W(m,2,(none,1),digit((none,1))), W({},2,({'m':6},53),NIL))
PH['N2s']=(W(m,2,(none,1),NIL), W({},2,({'m':6},41),NIL))
if __name__=='__main__':
    for w in sys.argv[1:]:
        s,t=PH[w]
        drive(w,s,t,matchers=(),maxev=300,verbose=True)
