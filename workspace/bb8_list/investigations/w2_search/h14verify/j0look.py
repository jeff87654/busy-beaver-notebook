import sys
from sim import *
def j0(k, w, f, tm=H14):
    word = fare(k) + bword([0] + [1]*w, f)
    m = TM(tm, word)
    while m.steps < 10**7:
        if m.q == 'J' and m.t[m.h] == 0: break
        if not m.step(): return None
    return m
if __name__ == '__main__':
    k, w, f = map(int, sys.argv[1:4])
    m = j0(k, w, f)
    wd, rel, a = m.word()
    print('steps', m.steps, 'head rel', rel, 'wordlen', len(wd), 'farlen', len(fare(k)))
    print(wd[:rel], '[J]', fmt(tokens(wd[rel:])))
