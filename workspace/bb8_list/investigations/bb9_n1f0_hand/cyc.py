"""cyc.py LOG: detect an eventual translated cycle in a kf jump log (token lists + k, ignoring step/seg/t/junk/r)."""
import sys, re
L = [l for l in open(sys.argv[1]) if l.startswith('J')]
keys, ts = [], []
for l in L:
    m = re.match(r'J\d+ (\w+) step=\d+ seg=\d+ t=(\d+) junk=(\d+) ntok=(\d+) r=\d+ \| (.*)', l)
    keys.append((m.group(1), m.group(4), m.group(5).strip())); ts.append(int(m.group(2)))
n = len(keys)
best = None
for p in range(1, n // 3):
    i = n - 1
    while i - p >= 0 and keys[i] == keys[i - p]: i -= 1
    run = n - 1 - i
    if run >= 2 * p and (best is None or run > best[1] + p):
        best = (p, run)
if best:
    p, run = best; s = n - run - p
    print(f'jumps={n}: periodic with period {p} jumps over the last {run} jumps (from J{s+1}); t grows by {ts[-1]-ts[-1-p]} per period')
    ks = [k[2].split('k=')[-1] if k[0]=='CL' else 'R1' for k in keys[n-p:]]
    print('  cleared k per period:', ' '.join(x for x in ks if x != 'R1'))
else:
    print(f'jumps={n}: no translated cycle found')
