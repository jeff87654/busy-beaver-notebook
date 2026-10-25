import sys
sys.path.insert(0,'.')
import planner8 as pl
from planner8 import *
# concrete: left = 1 (01)^4 1 1 (01)^10 ; G at blank
w='1'+'01'*4+'1'+'1'+'01'*10
L=[int(c) for c in reversed(w)]+[BLANK]
cfg=('G',L,[BLANK],'>')
n=0
for i in range(400):
    try: cfg=step(cfg)
    except Exception as e: print('exc',e); break
    n+=1
    if n in (1,95,100,205,210,211): print(n,show(cfg))
print(n,show(cfg))
