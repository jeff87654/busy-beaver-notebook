import sys, time
from ms import *
Yk = cfgB(['101' * 13, ('R', '10', 'k'), '11', '01', '00', TAIL])
Yt = cfgB(['101' * 13, '11', ('R', '0101', 'k'), '01', '00', TAIL])
if __name__ == "__main__":
  pl.LEMMAS.clear()
  t0 = time.time()
  try:
      tree = mexp.explore(Yk, Yt, splits=int(sys.argv[1]))
      print('OK %.1fs' % (time.time() - t0))
      print('\n'.join(mexp.describe(tree))[:5000])
  except Exception as e:
      print('FAILED %.1fs' % (time.time() - t0), str(e)[:1500])
