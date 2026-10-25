import sys
sys.path.insert(0,'.')
import planner8 as pl
from planner8 import *
def run(cnt,blk=(1,0)): return ('run',tuple(blk),lin({cnt:1}))
tail=[1,0]*4+[run('T')]
start=('G',tail+[1,1]+[1,0]*3+[run('A'),1,V('l')],[BLANK],'>')
target=('G',[1,0,1,0,1]+[1,0]*7+[run('T'),1,run('A'),1,V('l')],[BLANK],'>')
s,c=drive('FINAL',start,target,maxev=100)
print(s)
