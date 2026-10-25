"""period.py: literal grid checks of the six n1 period stages against the symbolic period map"""
from st import *
from fardec import dec
import sys, time
def tl(s): return expand(s)
bad = 0; t0 = time.time()
def chk(name, far, inp, exp_far, exp_toks):
    global bad
    r = stage(far, inp)
    ok = r['kind'] == 'K' and dec(r['far']) == exp_far and r['toks'] == exp_toks
    if not ok:
        bad += 1
        print(f"MISMATCH {name}: got {fmt(r)[:120]} | far={dec(r.get('far',''))}")
    return r
Rs = [19, 2539] if '--big' in sys.argv else [19]
ks = [1, 3, 4, 7]
ns = [5, 6, 7, 32, 33, 100, 101]
# G1: [2^k 5 1^m 0^3 1 P 0 1^n | 1 | R] -> far D2^(k+2) D5 D1^(m-6) D0^2 <100> [2 (2R+3) 1^(n+(2P+1)/3) | 1 | 1]
cnt = 0
for k in ks:
    for m in [7, 8, 9, 15, 71, 200]:
        for n in ns:
            for P in [40, 5080]:
                for R in Rs:
                    chk('G1', '', tl(f"2^{k} 5 1^{m} 0^3 1 {P} 0 1^{n}") + [1, R],
                        f"D2^{k+2} D5 D1^{m-6} D0^2 <100>" if m - 6 > 1 else f"D2^{k+2} D5 D1 D0^2 <100>",
                        tl(f"2 {2*R+3} 1^{n+(2*P+1)//3}") + [1, 1]); cnt += 1
print('G1 done', cnt, 'bad', bad, time.time()-t0)
# S2: far + [2 2 1^n | 1 | R] -> [2^k 5 1^m 0^2 (2R+7) 1^n | 1 | 2]  (far = D2^k D5 D1^m D0^2 <100>)
cnt = 0
for k in [3, 5, 9]:
    for m in [1, 2, 3, 9, 65]:
        for n in ns:
            for R in Rs:
                far = '10101' * k + '10101010101' + '101' * m + '11' + '100'
                chk('S2', far, tl(f"2 2 1^{n}") + [1, R], '', tl(f"2^{k} 5 1^{m} 0^2 {2*R+7} 1^{n}") + [1, 2]); cnt += 1
print('S2 done', cnt, 'bad', bad, time.time()-t0)
# S3: [2^k 5 1^m 0^2 P 3 1^n | 1 | R] -> [2^k 5 1^m 0^2 P 0 (2R+5) 1^(n-1) | 1 | 1]
cnt = 0
for k in [3, 5]:
    for m in [1, 3, 65]:
        for n in ns:
            for P in [42, 5082]:
                for R in Rs:
                    chk('S3', '', tl(f"2^{k} 5 1^{m} 0^2 {P} 3 1^{n}") + [1, R], '', tl(f"2^{k} 5 1^{m} 0^2 {P} 0 {2*R+5} 1^{n-1}") + [1, 1]); cnt += 1
print('S3 done', cnt, 'bad', bad, time.time()-t0)
# G2: [2^k 5 1^m 0^2 P 0 1^n | 1 | R] -> [2^k 5 1^(m-2) 0^2 (2R+3) 1^(n+(2P+3)/3) | 1 | 1]
cnt = 0
for k in [3, 5]:
    for m in [3, 4, 5, 9, 63]:
        for n in ns:
            for P in [42, 5082]:
                for R in Rs:
                    chk('G2', '', tl(f"2^{k} 5 1^{m} 0^2 {P} 0 1^{n}") + [1, R], '', tl(f"2^{k} 5 1^{m-2} 0^2 {2*R+3} 1^{n+(2*P+3)//3}") + [1, 1]); cnt += 1
print('G2 done', cnt, 'bad', bad, time.time()-t0)
# S5: [2^k 5 1^m 0^2 2 1^n | 1 | R] -> [2^(k+2) 5 1^(m-6) 0^3 1 (2R+5) 1^n | 1 | 2]
cnt = 0
for k in [3, 5]:
    for m in [7, 8, 9, 15, 63]:
        for n in ns:
            for R in Rs:
                chk('S5', '', tl(f"2^{k} 5 1^{m} 0^2 2 1^{n}") + [1, R], '', tl(f"2^{k+2} 5 1^{m-6} 0^3 1 {2*R+5} 1^{n}") + [1, 2]); cnt += 1
print('S5 done', cnt, 'bad', bad, time.time()-t0)
# S6: [2^k 5 1^m 0^3 1 P 3 1^n | 1 | R] -> [2^k 5 1^m 0^3 1 P 0 (2R+5) 1^(n-1) | 1 | 1]
cnt = 0
for k in [3, 5]:
    for m in [1, 3, 57]:
        for n in ns:
            for P in [40, 5080]:
                for R in Rs:
                    chk('S6', '', tl(f"2^{k} 5 1^{m} 0^3 1 {P} 3 1^{n}") + [1, R], '', tl(f"2^{k} 5 1^{m} 0^3 1 {P} 0 {2*R+5} 1^{n-1}") + [1, 1]); cnt += 1
print('S6 done', cnt, 'bad', bad, time.time()-t0)
print('TOTAL bad', bad)
