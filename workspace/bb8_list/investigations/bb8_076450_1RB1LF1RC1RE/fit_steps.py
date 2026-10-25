"""Check closed-form step counts against every literal count recorded by check_rules.py (check_rules.json).
  P (n = 2p even, n >= 4):   4n + 29
  R (n = 2p+1 odd, n >= 3):  4n + 56
  C (n = 6j+5):              4n + 47 = 24j + 67
  Wstep  W(j,m+1) -> W(2j+2,m):  (24j+67) + sum_{i=1}^{2j+2} (24i+29) = (24j+67) + (2j+2)(24j+65)
  Wreset W(j,0)   -> W(0,6j+7):  4(6j+5) + 56 = 24j + 76
"""
import json
d = json.load(open('check_rules.json'))['results']
F = {
    'P': lambda p: 4 * (2 * p) + 29,
    'R': lambda p: 4 * (2 * p + 1) + 56,
    'C': lambda j: 24 * j + 67,
}
bad = tot = 0
for k, f in F.items():
    for p, s in d[k]['steps'].items():
        tot += 1
        if f(int(p)) != s:
            bad += 1; print('MISMATCH', k, p, s, f(int(p)))
def wstep(j): return (24 * j + 67) + (2 * j + 2) * (24 * j + 65)
def wreset(j): return 24 * j + 76
for key, s in d['Wstep']['steps'].items():
    j, m = map(int, key.split(','))
    tot += 1
    if wstep(j) != s:
        bad += 1; print('MISMATCH Wstep', key, s, wstep(j))
for key, s in d['Wreset']['steps'].items():
    tot += 1
    if wreset(int(key)) != s:
        bad += 1; print('MISMATCH Wreset', key, s, wreset(int(key)))
print('%d step counts checked, %d mismatches' % (tot, bad))
