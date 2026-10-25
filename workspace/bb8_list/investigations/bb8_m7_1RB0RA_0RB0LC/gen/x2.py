import sys
from x1 import *
if __name__ == '__main__':
    cfgx = M2
    depth=int(sys.argv[2]) if len(sys.argv)>2 else 2
    print(show(cfgx))
    for it in range(int(sys.argv[1])):
        try:
            ops,cf,how=mexp.run_stuck(cfgx,None)
        except Exception as e:
            print('run_stuck exc',repr(e)[:300]); break
        print(it,'run_stuck',how,len(ops),show(cf)[:260])
        lp=mexp.find_loop(cf,depth,verbose=False)
        if lp is None:
            print('  NO LOOP'); break
        cfgx=lp.after()
        print('  loop ok ->',show(cfgx)[:260])
