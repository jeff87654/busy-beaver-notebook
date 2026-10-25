import sys
from ev import parse, rl
prev=None; want=False
for line in sys.stdin:
    p=line.split()
    if not p or not p[0].isdigit(): print(line.strip()); continue
    pre,d=parse(p[1:])
    if pre!=1: continue
    s='%s | %s'%(p[0],rl(d))
    small = len(d)<2 or (isinstance(d[1],int) and d[1]<=1)
    if small or want:
        if not want and prev: print(prev)
        print(s)
        if not small: print('--')
    want=small; prev=s
