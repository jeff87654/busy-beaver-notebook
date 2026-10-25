import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from common import *
z = zf2.ZF2(); z.AXIOMORDER = AXIOMORDER; z.build_machine()
f, d, t, fw = count(z.tm)
print(f, d, t); print(fw)
z.tm.save(HERE + r'\base.tm')
