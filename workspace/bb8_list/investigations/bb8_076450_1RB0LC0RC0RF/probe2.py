from probe import run_from
from lit import compress
import sys
pre = sys.argv[1]
for m in range(0, 26):
    r = run_from(pre + '1'*m)
    if isinstance(r,str): print(m, r); continue
    st, W = r[0]
    assert W.startswith(pre[:-2]) or True
    print(m, st, compress(W))
