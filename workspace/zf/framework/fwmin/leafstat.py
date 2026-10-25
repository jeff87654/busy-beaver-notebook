import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\zf\framework\fwmin')
from common import *
from collections import Counter
z = zf2.ZF2(); z.AXIOMORDER = AXIOMORDER; z.build_machine()
c = Counter()
for i in z.reachable():
    s = z.sequences[i].seq
    for pos, v in enumerate(s):
        if isinstance(v, str): c[(v, pos)] += 1
for k in sorted(c): print(k, c[k])
