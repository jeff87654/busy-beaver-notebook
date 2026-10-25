import sys, time
from ms import *
a, b = MS[sys.argv[1]], MS[sys.argv[2]]
cf = a
for it in range(int(sys.argv[3])):
    ops, cf, how = mexp.run_stuck(cf, b)
    print(it, how, sum(o[1] for o in ops if o[0] == 'steps'), show(cf)[:700])
    if how != 'stuck': break
    lp = mexp.find_loop(cf, 2)
    if lp is None:
        print('no loop'); break
    print('  loop on', lp.v_at, 'X =', show(lp.X)[:500])
    cf = lp.after()
    print('  after', show(cf)[:500])
