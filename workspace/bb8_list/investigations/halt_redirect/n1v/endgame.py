from st import *
from fardec import dec
import sys
Rs = [19, 2539] if '--big' in sys.argv else [19]
print("== exhaustion G1 (m=1): [2^k 5 1 0^3 1 P 0 1^n | 1 | R]")
fars = {}
for k in [3, 7, 23, 24, 47, 95]:
    for n in [5, 32, 302, 303]:
        for P in [40, 5080]:
            for R in Rs:
                r = stage('', expand(f"2^{k} 5 1 0^3 1 {P} 0 1^{n}") + [1, R])
                print(f"k={k} n={n} P={P} R={R}: {fmt(r)[:40]} far={dec(r.get('far',''))} step={r.get('step')}")
                fars[(k,n,P,R)] = r.get('far','')
print("== S36: far + [3 1^n | 1 | R] and S37: far + [0 1^n | 1 | R]")
for k in [3, 23, 47]:
    far = fars[(k, 32, 40, 19)]
    for n in [5, 32, 329, 330]:
        for R in Rs:
            r = stage(far, expand(f"3 1^{n}") + [1, R])
            print(f"S36 k={k} n={n} R={R}: {fmt(r)[:40]} far={dec(r.get('far',''))} step={r.get('step')}")
            r = stage(far, expand(f"0 1^{n}") + [1, R])
            print(f"S37 k={k} n={n} R={R}: {fmt(r)[:60]} step={r.get('step')}")
