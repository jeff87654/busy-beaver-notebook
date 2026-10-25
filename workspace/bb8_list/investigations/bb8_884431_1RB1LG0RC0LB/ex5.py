import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
# zero list tail: B> 000 (11)^b 0^(n+2) 1 blank   (gap = n+2 zeros incl. separators, here n = count of zero digits - 1 +...) 
R=[0,0,0]+mkrun(U,{'b':1})+[0,0,0,0,0,0]+mkrun((0,),{'n':1})+[1,BLANK]
stop=lambda cfg: cfg[0]=='H'
drive('Zstart',('B',[BLANK],R,'>'),None,maxev=40,stop_at=stop)
