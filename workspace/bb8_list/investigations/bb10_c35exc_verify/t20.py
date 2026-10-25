from lib import *
def first(toks, N=10**6):
    bf, end = bforms(M10, toks, N, maxsnap=2)
    if len(bf) > 1:
        return bf[1][1], bf[1][0]
    return None, end
P = [2, 1, 1, 0, 2, 1, 0, 1]
for s in (0, 2):
  for w in [0, 1, 2, 3, 4, 5, 6, 7]:
    for k in (0, 1, 2):
      for y in (4, 5, 6):
        toks = P + [10] + [w, s] + [1] * k + [0, y]
        t, info = first(toks)
        if t is None:
            print('s=%d w=%d k=%d y=%d' % (s, w, k, y), ctok(toks[8:]), '-> NONE', info[0], info[1])
        else:
            kk, a1, a2 = diff(toks, t)
            print('s=%d w=%d k=%d y=%d' % (s, w, k, y), ctok(a1), '->', ctok(a2), ' [%d]' % info)
