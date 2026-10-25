"""For the growth halters: compare crossed lengths with all post-start accumulators represented by r = 19 vs r = 31
(FIXREP).  If the growth step changes, the run grows by accumulator-sized steps (f_(omega+1)-type)."""
import sys, threading
sys.setrecursionlimit(200000)
threading.stack_size(256 * 1024 * 1024 - 4096)
import mf35
ms = [l.split()[0] for l in open('growth_halters.txt') if l.strip()]
def main():
    for m in ms:
        res = []
        for rv in (19, 31):
            mf35.FIXREP = rv; mf35._CACHE.clear()
            k, h = mf35.follow(m, 'A', 400, 200_000_000)
            zs = [z for z in (mf35.zeros_of(x) for x in h if x.startswith('J')) if z is not None]
            res.append((rv, k, len(h), zs[:18], h[-1]))
        print(m[56:], file=sys.stdout)
        for r in res:
            print('   r=%d %s stages=%d %s %s' % r, flush=True)
t = threading.Thread(target=main); t.start(); t.join()
