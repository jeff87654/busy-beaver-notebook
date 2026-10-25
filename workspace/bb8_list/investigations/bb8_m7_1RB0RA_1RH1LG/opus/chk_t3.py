import sys
from sim import *
c, a1, a2 = '110', '10', '1010'
TAILC = c + '1111' + c + '0' + a1 + '0' + '1'
for b in range(0, 5):
    r = 3*b+2
    j = 13
    tgt = a2 + '1' + c + '0' + (a1 + '0') * (3*r) + a1 + '11' + (c + '001') * ((j-3)//2) + c + '0' + TAILC
    cf = Cfg(used(12, b))
    found = None
    while cf.steps < 10**6:
        if cf.step(): print('halt'); break
        if cf.st == 'B' and cf.h == cf.hi and cf.tape[cf.h] == 0:
            L, R = cf.contents()
            if R == '' and L == tgt:
                found = cf.steps; break
    print(b, found)
