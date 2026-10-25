from st import *
import itertools
print("== G1: [2^3 5 1^71 0^3 1 P 0 1^32 | 1 | R]")
for P in (40, 5080, 10120, 50440):
    for R in (19, 2539):
        r = stage('', expand(f"2^3 5 1^71 0^3 1 {P} 0 1^32") + [1, R])
        print(f"P={P} R={R}: {fmt(r)[:60]} step={r.get('step')} farlen={len(r.get('far',''))}")
print("== G2: [2^5 5 1^65 0^2 P 0 1^58 | 1 | R]")
for P in (42, 5082, 10122, 50442):
    for R in (19, 2539):
        r = stage('', expand(f"2^5 5 1^65 0^2 {P} 0 1^58") + [1, R])
        print(f"P={P} R={R}: {fmt(r)[:60]} step={r.get('step')} farlen={len(r.get('far',''))}")
print("== D3->D0 (a): [2^5 5 1^65 0^2 P 3 1^58 | 1 | R]")
for P in (42, 5082, 10122):
    for R in (19, 2539):
        r = stage('', expand(f"2^5 5 1^65 0^2 {P} 3 1^58") + [1, R])
        print(f"P={P} R={R}: {fmt(r)[:60]} step={r.get('step')} farlen={len(r.get('far',''))}")
print("== D3->D0 (b): [2^7 5 1^57 0^3 1 P 3 1^86 | 1 | R]")
for P in (40, 5080, 10120):
    for R in (19, 2539):
        r = stage('', expand(f"2^7 5 1^57 0^3 1 {P} 3 1^86") + [1, R])
        print(f"P={P} R={R}: {fmt(r)[:60]} step={r.get('step')} farlen={len(r.get('far',''))}")
