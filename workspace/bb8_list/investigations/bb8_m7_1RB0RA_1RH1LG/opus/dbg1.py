import sys, time
from ms import *
from ms2 import Yk, Yt
ops, cf, how = mexp.run_stuck(Yk, Yt)
print(how, show(cf)[:400])
print([o[0] if o[0] != 'steps' else o[1] for o in ops][:60])
t0 = time.time()
mexp.debug_loop(cf, depth=1)
print('%.1fs' % (time.time() - t0))
