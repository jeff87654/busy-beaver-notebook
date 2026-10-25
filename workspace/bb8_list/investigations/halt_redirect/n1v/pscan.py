"""pscan.py: parked-token residue scan for the two unpack stages: P = 40 + 5040 t (G1) and 42 + 5040 t (G2),
t = 0..T, R = 19; covers every residue of the real P (6B+4 / 6B+6) mod 25, 27, 49, 11, 13 and mod 32.
Also the step count of G1 as a function of k and m (does the stage traverse the counter?)."""
from st import *
from fardec import dec
import sys
T = int(sys.argv[1]) if len(sys.argv) > 1 else 12
bad = 0
for t in range(T + 1):
    P = 40 + 5040 * t
    r = stage('', expand(f"2^3 5 1^15 0^3 1 {P} 0 1^32") + [1, 19], maxs=4e9)
    ok = r['kind'] == 'K' and r['toks'] == expand(f"2 41 1^{32 + (2*P+1)//3}") + [1, 1] and dec(r['far']) == 'D2^5 D5 D1^9 D0^2 <100>'
    P2 = 42 + 5040 * t
    r2 = stage('', expand(f"2^5 5 1^9 0^2 {P2} 0 1^58") + [1, 19], maxs=4e9)
    ok2 = r2['kind'] == 'K' and r2['toks'] == expand(f"2^5 5 1^7 0^2 41 1^{58 + (2*P2+3)//3}") + [1, 1] and not r2['far']
    bad += (not ok) + (not ok2)
    print(f"t={t} P={P} (mod 25/27/49/11/13/32 = {P%25},{P%27},{P%49},{P%11},{P%13},{P%32}): G1 {'ok' if ok else 'MISMATCH ' + fmt(r)[:80]} steps={r.get('step')}; "
          f"G2 P2={P2} {'ok' if ok2 else 'MISMATCH ' + fmt(r2)[:80]} steps={r2.get('step')}", flush=True)
print('bad', bad)
print('== G1 step counts vs k, m (P=40, R=19, n=32)')
for k in (1, 3, 7, 15, 31):
    for m in (7, 15, 71, 200, 500):
        r = stage('', expand(f"2^{k} 5 1^{m} 0^3 1 40 0 1^32") + [1, 19])
        print(f"k={k} m={m}: steps={r.get('step')} out={fmt(r)[:20]} far={dec(r.get('far',''))[:40]}")
print('== S5 step counts vs k, m (R=19, n=87)')
for k in (1, 3, 7, 15, 31):
    for m in (7, 15, 71, 200, 500):
        r = stage('', expand(f"2^{k} 5 1^{m} 0^2 2 1^87") + [1, 19])
        print(f"k={k} m={m}: steps={r.get('step')} out={fmt(r)[:40]}")
print('== G2 step counts vs k, m (P=42, R=19, n=58)')
for k in (1, 3, 7, 15, 31):
    for m in (3, 15, 71, 200, 500):
        r = stage('', expand(f"2^{k} 5 1^{m} 0^2 42 0 1^58") + [1, 19])
        print(f"k={k} m={m}: steps={r.get('step')} out={fmt(r)[:40]}")
