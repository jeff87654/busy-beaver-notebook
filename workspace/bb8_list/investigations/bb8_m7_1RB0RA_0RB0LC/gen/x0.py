import sys
from common import *
from shapes import *
import mexp
from mexp import show
U3 = (0, 1) * 3
START = ('B', tailpart() + accr(2) + [run(U3, b=1)] + tok(1) + [run(Z, n=1)] + [1, 1, BLANK], [BLANK], '>')
if __name__ == '__main__':
    cfgx = START
    print(show(cfgx))
    for it in range(int(sys.argv[1])):
        try:
            ops,cf,how=mexp.run_stuck(cfgx,None)
        except Exception as e:
            print('run_stuck exc',repr(e)[:300]); break
        print(it,'run_stuck',how,len(ops),show(cf)[:300])
        lp=mexp.find_loop(cf,int(sys.argv[2]),verbose=False)
        if lp is None:
            print('  NO LOOP'); break
        cfgx=lp.after()
        print('  loop ok ->',show(cfgx)[:300])
