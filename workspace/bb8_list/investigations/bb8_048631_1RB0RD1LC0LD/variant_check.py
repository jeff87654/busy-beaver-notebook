import sys
import fam
from fam import *
tm = sys.argv[1]
fam.TM = tm
import msim
m = MSim(tm)
a = asim.ASim(m)
n = 0
try:
    while n < 8 and a.nmacro < 10**7:
        a.step()
        r = match(m)
        if r:
            print(a.nmacro, m.steps, r, flush=True); n += 1
except Halt as h:
    print('HALT', h)
