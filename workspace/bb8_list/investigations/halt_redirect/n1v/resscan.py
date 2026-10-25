"""resscan.py: stage outputs for R = 19 + 2520 j, j = 0..J (varying the residues mod 16, 25, 27, 49, 11, 13, ...)"""
from st import *
from fardec import dec
import sys, time
J = int(sys.argv[1]) if len(sys.argv) > 1 else 2
J0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
for j in range(J0, J + 1):
    R = 19 + 2520 * j
    t0 = time.time()
    r = stage('', expand("2^3 5 1^15 0^3 1 40 0 1^32") + [1, R], maxs=4e9)
    g1 = fmt(r)[:40] + ' far=' + dec(r.get('far', ''))
    far = '10101' * 5 + '10101010101' + '101' * 9 + '11' + '100'
    r = stage(far, expand("2 2 1^59") + [1, R], maxs=4e9)
    s2 = fmt(r)[:60]
    r = stage('', expand("2^5 5 1^9 0^2 42 3 1^58") + [1, R], maxs=4e9)
    s3 = fmt(r)[:60]
    r = stage('', expand("2^5 5 1^7 0^2 2 1^87") + [1, R], maxs=4e9)
    s5 = fmt(r)[:60]
    r = stage('', expand("2^5 5 1^7 0^2 42 0 1^58") + [1, R], maxs=4e9)
    g2 = fmt(r)[:60]
    farx = '10101' * 17 + '101' + '101010101010100100000' + '101' + '11' + '100100100100100'
    r = stage(farx, expand("3 1^329") + [1, R], maxs=4e9)
    s36 = fmt(r)[:40]
    r = stage(farx, expand("0 1^329") + [1, R], maxs=4e9)
    s37 = fmt(r)[:60]
    r = stage('', expand("2^23 5 1 0^3 1 40 0 1^302") + [1, R], maxs=4e9)
    gx = fmt(r)[:40] + ' far=' + dec(r.get('far', ''))
    print(f"R={R}:\n  G1 {g1}\n  S2 {s2}\n  S3 {s3}\n  S5 {s5}\n  G2 {g2}\n  S36 {s36}\n  S37 {s37}\n  Gx {gx}\n  ({time.time()-t0:.0f}s)", flush=True)
