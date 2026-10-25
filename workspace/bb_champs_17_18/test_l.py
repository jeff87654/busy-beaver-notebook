import sys
from machines import *
from cfg import *
M = globals()[sys.argv[1]]; H = sys.argv[2]
def one(n): return '1'*n
for A in [3,4,7]:
  for p in [1,2]:
    for d in [0,1,2,3,4,5]:
      for tail in ['', '0'+one(4), '0'+one(4)+'0'+one(3)]:
        s = build(M, one(A)+'01'*p+'0', H, '0'+one(d)+tail+'0')
        r = run_until(s, lambda s: s.st=='B' and s.face=='R' and len(s.L)==1 and s.L[0]==[1,3] and s.steps>0, 10**6)
        l, rr = norm(*cells(s))
        print(f"A={A} p={p} d={d} tail={[len(x) for x in tail.split('0')[1:]]} -> {r} steps={s.steps} {l} B> {[len(x) for x in rr.split('0')]}")
