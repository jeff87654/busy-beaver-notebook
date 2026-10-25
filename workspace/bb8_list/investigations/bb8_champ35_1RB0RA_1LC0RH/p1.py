import sys
sys.path.insert(0,'.')
import planner8 as pl
from planner8 import *
U=(1,0)
def run(cnt,blk=U): return ('run',tuple(blk),lin({cnt:1}))
def run0(): pass
# round: l 1 (01)^(N+1) 1 (01)^T  G>  ->  l 1 (01)^N 1 (01)^(T+2) G>
Lstart=[run('T'),1,1,0,run('N'),1,run('A'),1,V('l')]
Lstart=[run('T'),1]+[1,0]+[run('N'),1]+[run('A'),1,V('l')]
# careful: nearest-first. tail (01)^T nearest-first = (1,0) repeated, then separator 1, then b-run (01)^(N+1), then 1, then a-run
start=('G',[run('T'),1,1,0,run('N'),1,run('A'),1,V('l')],[BLANK],'>')
target=('G',[1,0,1,0,run('T'),1,run('N'),1,run('A'),1,V('l')],[BLANK],'>')
s,c=drive('ROUND',start,target)
