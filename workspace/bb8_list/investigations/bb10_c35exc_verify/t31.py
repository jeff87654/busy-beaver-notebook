from lib import *
import re
P = [2, 1, 1, 0, 2, 1, 0, 1]
toks = P + [40] + [30, 3, 1, 1, 0, 0, 13]
w = word(toks)
for n in (10**6, 3 * 10**6, 10**7, 3 * 10**7, 10**8):
    snaps, end = run(M10, w, 'G', '0', n)
    L, S, R = end[2], end[3], end[4]
    m = max((len(x) for x in re.findall('1+', L)), default=0)
    print(n, 'tapeL', len(L), 'max 1-run', m, 'state', S, 'right', R[:30], 'leftprefix same?', L.lstrip('0').startswith(w.lstrip('0')[:200]))
