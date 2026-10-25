import sys, time
from ms import *
from ms2 import Yk, Yt
ops, cf, how = mexp.run_stuck(Yk, Yt)
lp = mexp.find_loop(cf, 1)
af = lp.after()
print('after loop:', show(af)[:500])
ops, cf2, how = mexp.run_stuck(af, Yt)
print(how, show(cf2)[:500])
print('target   :', show(Yt)[:500])
