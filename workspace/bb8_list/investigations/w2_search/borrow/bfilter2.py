"""bfilter2.py TSV: RS leaves whose prefix P has a last digit x >= 3 followed only by tokens < 3 (any x); prints them
as 'cand MACHINE' lines for bverify2 (which checks that x moves with the start digit d)."""
import idle  # noqa: F401  (Idle priority)

import sys
from ilib import expand
for f in sys.argv[1:]:
    for l in open(f):
        x = l.rstrip('\n').split('\t')
        if x[1] != 'RS' or not x[3]: continue
        P = expand(x[3])
        idx = [i for i, v in enumerate(P) if v >= 3]
        if not idx: continue
        j = idx[-1]
        print('cand', x[0], P[j], x[3], x[4])
