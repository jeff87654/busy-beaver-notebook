"""Literal checks of the champion rules R1/R2/R3 of the 1LD1LC machine in the contexts of its run, via reach2.exe.
  R1: [L | a | r] -> [L | a-3 | 2r+5]            a >= 4, any r
  R2: [L, d | 1 | r] -> [L, d-3 | 2r+5 | 1]      d >= 3, any r
  R3: [L, d, 1^z | 1 | r] -> [L, d-3, 2r+5, 1^(z-1) | 1 | 1]   d >= 3, z >= 1, any r
Every job must print REACHED, else FAIL (HALT / TIMEOUT / another configuration).
usage: python rules.py [MAXSTEPS]"""
import sys, subprocess, itertools
sys.path.insert(0, r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect/v1LD1LC')
from lit1 import M, expand, F
TAIL = F['SUF']
HR = r'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/halt_redirect'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)

def word(toks):
    return ''.join('10' * m + '1' for m in toks) + TAIL

CONTEXTS = ['9^3', '9^3 8', '9^2 5 3 0 3 38', '9^2 5 3 0 3 38 0', '9^2 2 7 0 0 3 3 0 3 0 3 0', '9^2 2 7 0 0 3 3 0 3 0 3 0 38 0',
            '9^2 2 7 0 0 3 3 0 3 0 0 5 1 0 1 0 1 0 0 1 1 7 1 1 0 3 3 0 3 0 3 0', '9^2 2 7 0 0 3 3 0 0 5 1 0 0 1 1 7 1 1 0 3 3 0 3 0 2 1 1 43 1 1 1 1 0 0',
            '9^2 2 7 0 0 3 3 0 0 5 1 0 0 1 1 7 1 1 0 3 3 0 3 0 2 1 1 43 1 0 1', '', '2 7 0 0 3 3 0 3 0 2 1 1 5083 1 1 1 1 0 0']
DS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 38, 41, 43, 44, 45, 2*2539+3, 2*2539+5]
RS = [1, 2, 3, 4, 5, 7, 19, 40, 2539]
AS = [4, 5, 6, 7, 9, 10, 43, 2*2539+5]
ZS = [1, 2, 3, 5, 10, 67, 1075]

jobs = []
for L in CONTEXTS:
    Lt = expand(L)
    for a, r in itertools.product(AS, RS):
        jobs.append((f'R1|{L}|a={a}|r={r}', word(Lt + [a, r]), word(Lt + [a - 3, 2 * r + 5])))
    for d, r in itertools.product(DS, RS):
        jobs.append((f'R2|{L}|d={d}|r={r}', word(Lt + [d, 1, r]), word(Lt + [d - 3, 2 * r + 5, 1])))
    for d, z, r in itertools.product(DS, ZS, RS):
        if z > 100 and (d > 100 or r > 100):
            continue
        jobs.append((f'R3|{L}|d={d}|z={z}|r={r}', word(Lt + [d] + [1] * z + [1, r]), word(Lt + [d - 3, 2 * r + 5] + [1] * (z - 1) + [1, 1])))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000_000
with open('rules_jobs.txt', 'w') as f:
    for lab, w0, w1 in jobs:
        f.write(f'{lab.replace(" ", "_")} {w0} {len(w0)} G {w1} G\n')
out = subprocess.run([HR + '/reach2.exe', M, 'rules_jobs.txt', str(N)], capture_output=True, text=True, creationflags=LOW).stdout
res = [l.split('\t') for l in out.strip().splitlines()]
bad = [l for l in res if len(l) < 2 or l[1] != 'REACHED']
print(f'RULES {len(jobs)} jobs, {len(res)} results, {len(bad)} not REACHED')
for l in bad[:30]:
    print('FAIL', l)
if len(res) != len(jobs) or bad:
    sys.exit(1)
