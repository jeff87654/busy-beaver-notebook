"""Run the explorer from W(w+P, 0, 10k+c zeros) and stop at the first W-form (state D, boundary 1 1 1 0 1 1 0 0 1 D>)
reached after the refill.  Prints it and pickles it."""
import sys, pickle
from parts import *
c = int(sys.argv[1]); prew = int(sys.argv[2])
S = W2(dict(w=1), None, dict(k=1), pre_w=prew, beyond=[1, V('l')], extra_zeros=c, zblk=10)
BND = [1, 0, 0, 1, 1, 0, 1, 1, 1]
def is_w(cfg):
    q, L, R, mode = cfg
    return q == 'D' and mode == '>' and list(L[:9]) == BND
cfg = S
first = True
found = None
for it in range(400):
    # single-step until stuck, checking W-form after each literal step
    ops, cfg2, how = mexp.run_stuck(cfg, None)
    # re-run literally step by step to catch W-forms inside this stretch
    c2 = cfg
    n = 0
    hit = None
    for o in ops:
        if o[0] == 'steps':
            for _ in range(o[1]):
                c2 = pl.step(c2); n += 1
                if is_w(c2) and not first:
                    hit = c2; break
                first = False
            if hit: break
        else:
            break
    if hit:
        found = hit; break
    if how != 'stuck':
        print(how, pl.show(cfg2)); break
    lp = mexp.find_loop(cfg2, 2)
    if lp is None:
        print('NO LOOP at', pl.show(cfg2)); break
    cfg = lp.after()
    if is_w(cfg):
        found = cfg; break
if found:
    print('W-form:', pl.show(found))
    pickle.dump(found, open('H1_target_%d.pkl' % c, 'wb'))
