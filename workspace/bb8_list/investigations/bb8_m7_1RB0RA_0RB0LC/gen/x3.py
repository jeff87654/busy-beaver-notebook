import sys, time
from x1 import *
B100 = (1,0,0)
B12 = B100*12
M3 = ('B', [1,0,0,1,0,0] + [run((1,1,1), n=1)] + [1]*7 + [0,0] + [run(B12, b=1)] + list(B100)*7 + [1,1,1] + [0,1,0,1] + [BLANK], [BLANK], '>')
if __name__ == '__main__':
    pl.LEMMAS.clear()
    t0=time.time()
    pos = frozenset(sys.argv[1].split(',')) if len(sys.argv)>1 and sys.argv[1]!='-' else frozenset()
    try:
        tree = mexp.explore(M2, M3, positive=pos)
        print('explore OK %.1fs'%(time.time()-t0))
        print('\n'.join(mexp.describe(tree))[:2500])
    except Exception as e:
        import traceback; traceback.print_exc(limit=4)
        print('FAILED', repr(e)[:400])
