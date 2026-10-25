import sys
sys.path.insert(0,'.')
import gen_p0 as g
import planner8 as pl
name=sys.argv[1]
st,tg=g.PH[name]
pl.LEMMAS.clear()
script,c=pl.drive(name,st,None,maxev=400,verbose=True)
print(script[-3:])
print(pl.show(c))
