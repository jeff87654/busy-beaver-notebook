import sys
from fam import *
if __name__ == '__main__':
    s = Sim(TM)
    N = int(sys.argv[1]); lim = int(sys.argv[2])
    n = 0
    prev = None
    while s.steps < N and n < lim:
        r = fam_at(s)
        if r is not None and r[-1] % 2 == 1 and len(r) >= 2:
            print(s.steps, r[:-2], 'a=%d' % r[-2], 'b=%d' % ((r[-1]-1)//2)); n += 1
        if not s.step(): print('halt'); break
