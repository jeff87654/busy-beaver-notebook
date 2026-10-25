import sys, os, time
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine
pl.set_tm(TM)
nm=sys.argv[1]
s,t=rules()[nm]
orig=engine.explore
def tr(start,target,depth=2,splits=4,path='root',positive=frozenset()):
    print('ENTER',path,'%.1f'%(time.time()-T0),flush=True)
    r=orig(start,target,depth,splits,path,positive)
    print('DONE ',path,'%.1f'%(time.time()-T0),flush=True)
    return r
engine.explore=tr
T0=time.time()
tree=engine.explore(s,t,depth=int(sys.argv[2]) if len(sys.argv)>2 else 2)
print('\n'.join(engine.describe(tree)))
