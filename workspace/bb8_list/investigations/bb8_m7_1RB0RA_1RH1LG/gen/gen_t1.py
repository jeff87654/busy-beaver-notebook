import sys, time, traceback
from gen_cyc import *
I1 = cfg([('R', a1 * 6, 'b'), a1 * 4, '0', '1', c, '0', a1, '0', '1'])
I2 = cfg([a2, '1', c, '0', ('R', (a1 + '0') * 9, 'b'), (a1 + '0') * 10, '11', c, '0', a1, '0', '1'])
I3 = cfg([c, a2, ('R', c * 12, 'b'), c * 4, '1', c, a1, '0', '1', c, '00', '1111', c, '0', a1, '0', '1'])
I4 = ITEMS['T1'][1]
STAGES = {'S1': (ITEMS['T1'][0], I1), 'S2': (I1, I2), 'S3': (I2, I3), 'S4': (I3, I4)}
if __name__ == '__main__':
    for name in sys.argv[1:]:
        s, t = STAGES[name]
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, splits=int(sys.argv[0] and 1))
            print(name, 'OK', '%.1fs' % (time.time() - t0), flush=True)
        except Exception as e:
            print(name, 'FAILED', str(e)[:200].replace('\n', ' '), flush=True)
