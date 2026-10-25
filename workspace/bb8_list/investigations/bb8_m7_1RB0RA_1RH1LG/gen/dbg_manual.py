import sys
from gen_cyc import *
import mexp
from mexp import show
blk=sys.argv[1]; x=sys.argv[2]
J1=cfg([('R', blk, x), '0','1', c,'0',a1,'0','1'])
cfgx=J1
for it in range(int(sys.argv[3])):
    ops,cf,how=mexp.run_stuck(cfgx,None)
    print(it,'run_stuck',how,show(cf)[:260])
    lp=mexp.find_loop(cf,int(sys.argv[4]),verbose=True)
    if lp is None:
        print('  NO LOOP'); break
    cfgx=lp.after()
    print('  loop ok ->',show(cfgx)[:260])
