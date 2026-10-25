import sys, time
from gen_cyc import *
# phase A: (10)^(2y) 0 1 c 0 a1 0 1  ->  a2 1 c 0 (a1 0)^(3y+4) 11 c 0 a1 0 1
J1 = cfg([('R', a1 * 2, 'y'), '0', '1', c, '0', a1, '0', '1'])
J2 = cfg([a2, '1', c, '0', ('R', (a1 + '0') * 3, 'y'), (a1 + '0') * 4, '11', c, '0', a1, '0', '1'])
# phase B with y = z+1:  a2 1 c 0 (a1 0)^(3z+7) 11 c 0 a1 0 1  ->  c a2 c^(4z) 1 c a1 0 1 c 00 1111 c 0 a1 0 1
K2 = cfg([a2, '1', c, '0', ('R', (a1 + '0') * 3, 'z'), (a1 + '0') * 7, '11', c, '0', a1, '0', '1'])
K3 = cfg([c, a2, ('R', c * 4, 'z'), '1', c, a1, '0', '1', c, '00', '1111', c, '0', a1, '0', '1'])
ST = {'A': (J1, J2), 'B': (K2, K3)}
if __name__ == '__main__':
    for name in sys.argv[1:]:
        s, t = ST[name]
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, splits=int(0))
            print(name, 'OK', '%.1fs' % (time.time() - t0), flush=True)
        except Exception as e:
            print(name, 'FAILED', str(e)[:300].replace('\n', ' '), flush=True)
