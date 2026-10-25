import sys
from machines import *
from cfg import *
M = globals()[sys.argv[1]]; H = sys.argv[2]   # H = name of the H-layer state (BB17: H, BB18: I)
def one(n): return '1'*n
def blocks(r):
    # right part string -> list of block sizes (split on single zeros), stop at '00'
    out=[]; 
    return [len(x) for x in r.split('0')]
for A in [3,4,5,6,7,8,9,12,13]:
  for p in [1,2,3]:
    for c in [0,1,3]:
        d=5
        s = build(M, one(A)+'01'*p+'0', H, one(c)+'0'+one(d)+'0')
        r = run_until(s, lambda s: s.st=='B' and s.face=='R' and len(s.L)==1 and s.L[0]==[1,3] and s.steps>0, 10**6)
        l, rr = norm(*cells(s))
        print(f"A={A:2} p={p} c={c} -> {r} 111 B> {blocks(rr)}")
