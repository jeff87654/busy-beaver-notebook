import sys
from subr import visits, toks, rle, fmt
ds = eval(sys.argv[1]); a = int(sys.argv[2]); b = int(sys.argv[3]); N = int(sys.argv[4]); lim = int(sys.argv[5]) if len(sys.argv) > 5 else 200
vs = visits(ds, a, b, N, lim)
for s, w in vs:
    if w == 'HALT': print(s, 'HALT'); continue
    t, r = toks(w)
    print('%6d  %s |%s' % (s, fmt(rle(t)), r))
