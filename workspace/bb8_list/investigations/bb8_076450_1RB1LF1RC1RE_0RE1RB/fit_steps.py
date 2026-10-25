"""Check closed-form step counts against every literal count recorded by check_rules.py.
Usage: python fit_steps.py check_rules.json            (main machine, H0 = 0LC)
       python fit_steps.py check_rules_H0_1LD.json     (H0 variant, H0 = 1LD)
With offsets (p0, r0, c0) = (19, 34, 29) for the main machine and (21, 38, 33) for the H0 variant:
  P (n = 2p+1 odd, n >= 3):  4n + p0
  R (n = 2p even, n >= 2):   4n + r0
  C (n = 6j+4):              4n + c0 = 24j + 16 + c0
  Wstep  W(j,m+1) -> W(2j+2,m):  C(j) + sum_{i=0}^{2j+1} P(6i+5) = (24j+16+c0) + (2j+2)(24j+32+p0)
  Wreset W(j,0)   -> W(0,6j+7):  4(6j+4) + r0 = 24j + 16 + r0
"""
import json, sys
fn = sys.argv[1] if len(sys.argv) > 1 else 'check_rules.json'
dd = json.load(open(fn))
tm, d = dd['tm'], dd['results']
p0, r0, c0 = {'0LC1LC': (19, 34, 29), '1LD1LC': (21, 38, 33)}[tm[-6:]]
F = {
    'P': lambda p: 4 * (2 * p + 1) + p0,
    'R': lambda p: 4 * (2 * p) + r0,
    'C': lambda j: 24 * j + 16 + c0,
}
bad = tot = 0
for k, f in F.items():
    for p, s in d[k]['steps'].items():
        tot += 1
        if f(int(p)) != s:
            bad += 1; print('MISMATCH', k, p, s, f(int(p)))
def wstep(j): return (24 * j + 16 + c0) + (2 * j + 2) * (24 * j + 32 + p0)
def wreset(j): return 24 * j + 16 + r0
for key, s in d['Wstep']['steps'].items():
    j, m = map(int, key.split(','))
    tot += 1
    if wstep(j) != s:
        bad += 1; print('MISMATCH Wstep', key, s, wstep(j))
for key, s in d['Wreset']['steps'].items():
    tot += 1
    if wreset(int(key)) != s:
        bad += 1; print('MISMATCH Wreset', key, s, wreset(int(key)))
print('%s: %d step counts checked, %d mismatches' % (tm, tot, bad))
