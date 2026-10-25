# Verify BB17 engine rules on crafted tapes.
import random, sys
from machines import *
from cfg import *
M = globals()[sys.argv[1]] if len(sys.argv)>1 else BB17
def one(n): return '1'*n
def lst(ds): return '0'.join(one(d) for d in ds)
random.seed(1); bad=0; n=0
# Rule T (transfer): 1^A (01)^p B> 1^e 0 R  ->  1^3 B> (10)^(p-1) 1^(A+1) 0 1^(e-1) 0 R   (A>=3, p>=1, e>=2)
for _ in range(400):
    A = random.randint(3,40); p = random.randint(1,6); e = random.randint(2,12)
    tail = '0' + lst([random.randint(1,4) for _ in range(3)]) + '00' + one(3) + '0' + one(5)
    s = build(M, one(A) + '01'*p, 'B', one(e) + tail)
    # stop at first B visit with left == '111' exactly
    r = run_until(s, lambda s: s.st=='B' and s.face=='R' and len(s.L)==1 and s.L[0]==[1,3] and s.steps>0)
    got = norm(*cells(s)); exp = norm('111', '10'*(p-1) + one(A+1) + '0' + one(e-1) + tail)
    n+=1
    if r!='OK' or got!=exp: bad+=1; print('T FAIL', A,p,e,r, got[1][:80], exp[1][:80]) if bad<5 else None
print('rule T', n, 'cases', bad, 'fail')
# Rule S (scan): 1^3 B> 1^d 0 ... ; d>=2 -> 1^(3d) 01 B> ;  d==1 -> 1^3 01 B>
bad=0
for d in range(1,30):
    tail='0'+one(3)+'00'+one(2)
    s = build(M, '111', 'B', one(d)+tail)
    r = run_until(s, lambda s: s.st=='B' and s.face=='R' and s.L and s.L[-1]==[1,1] and len(s.L)>=2 and s.steps>0)
    got=norm(*cells(s)); exp=norm(one(3*d)+'01', tail[1:])
    if r!='OK' or got!=exp: bad+=1; print('S FAIL', d, got, exp)
print('rule S', bad, 'fail')
