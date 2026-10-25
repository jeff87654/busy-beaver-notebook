import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from passcfg import *
s,t=pass_rule()
print(pl.show(s),'=>',pl.show(t))
tree=engine.explore(s,t)
print('\n'.join(engine.describe(tree)))
