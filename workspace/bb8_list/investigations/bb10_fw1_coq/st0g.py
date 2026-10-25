"""Run the explorer from the stage-0 start and stop at the first K-moment (G on the blank right end, tail D2,
r = D1, a = D1); print it and pickle it as the stage-0 target."""
import pickle, sys
from parts import *
s = PARTS['ST0free'][0]
KHEAD = [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1]
def is_k(c):
    q, L, R, mode = c
    return q == 'G' and mode == '>' and R == [BLANK] and list(L[:11]) == KHEAD and L[11] == 1
def replay(cfg, ops):
    for o in ops:
        if o[0] == 'steps':
            for _ in range(o[1]):
                cfg = pl.step(cfg)
                if is_k(cfg):
                    return cfg, True
        elif o[0] == 'cross':
            r, why = pl.try_crossing(cfg)
            cfg = r[0]
        elif o[0] == 'align':
            cfg = pl.try_align(cfg)[0]
    return cfg, False
cfg = s
first = True
for it in range(2000):
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    c3, hit = replay(cfg, ops)
    if hit and not first:
        print('K-moment:', pl.show(c3))
        pickle.dump(c3, open('ST0_T.pkl', 'wb'))
        break
    first = False
    if how != 'stuck':
        print('ended', how); break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('NO LOOP', pl.show(cfg2)[-300:]); break
    cfg = lp.after()
