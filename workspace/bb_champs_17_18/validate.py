# Full machine vs model, on crafted starts the model resolves to HALT with small numbers.
from machines import *
from cfg import *
import model
def one(n): return '1'*n
ok=bad=skip=0
for M, H in [(BB17,'H'), (BB18,'I')]:
  for l in [[2],[1,2],[3],[2,2],[1,1],[4],[1,3],[2,1,1],[5],[1,1,2]]:
    for c in [0,1,2]:
      for d in [0,1,2,3,5]:
        ev = model.run(l, c, d, maxev=10, cap=5000)
        if ev[-1][0] != 'HALT': skip+=1; continue
        s = build(M, '111', 'B', '0'.join(one(x) for x in l) + '00' + one(c) + '0' + one(d) + '0')
        r = run_until(s, lambda s: False, 3*10**6)
        l_, r_ = norm(*cells(s)); A, p = ev[-1][1], ev[-1][2]
        if r=='HALT' and l_.startswith(one(A)+'01'*p): ok+=1
        else: bad+=1; print('MISMATCH', H, l, c, d, ev, r, l_[:50])
print('ok', ok, 'bad', bad, 'skipped(non-small)', skip)
