import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_fam import *
s = PSB(1, {'c': 1}, 0, {'d': 1}); t = PSB(0, {'c': 1}, 1, {'d': 1})
for c in range(0, 7):
    print(c, [d for d in range(3) if validate.reaches(s, t, {'c': c, 'd': d}, max_steps=5000) is not None])
