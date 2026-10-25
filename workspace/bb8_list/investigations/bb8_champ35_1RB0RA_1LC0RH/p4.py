from kk import *
# R2: K(ds, x+1; 0; b) -> K(ds, x; 2b+2; 0), after rounds: b-run empty, tail T+4
# l' 1 (01)^(X+3) 1 (01)^1 1 1 (01)^(T+4) G>
tail=U(4,'T')
start=('G',tail+[1,1]+U(1)+[1]+U(3,'X')+[1,V('l')],[BLANK],'>')
# target: l' 1 (01)^X 1 (01)^(T+7) 1 (01)^1 1 (01)^2 G>
target=('G',U(2)+[1]+U(1)+[1]+U(7,'T')+[1]+U(0,'X')+[1,V('l')],[BLANK],'>')
s,c=drive('R2FIN',start,target,maxev=200)
