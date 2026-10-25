"""Independent literal checks of the 9-state candidate 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA.
Tokens D(m) = (10)^m 1; configurations are words with the head on the blank right of them in state G.
Champion rules in D terms (tail D4):  R1 [L|m+3|r] -> [L|m|2r+6];  R2 [..,X+3|1|r] -> [..,X|2r+7|0];
R3 [..,Y+3,1^k|1|r] -> [..,Y,2r+7,1^(k-1)|1|0] (k >= 1)."""
import random, subprocess, sys
from pathlib import Path
import gen
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA'
def D(m): return '10' * m + '1'
def W(toks): return ''.join(D(t) for t in toks)
jobs = []
def add(lab, start, target):
    s, t = W(start), W(target)
    jobs.append(f'{lab} {s} {len(s)} G {t} G')
# (a) stage 0 from the literal exhausted list K(0^35;0;b)
for b in range(1, 200, 5):
    w = gen.C35['c35'][1]
    q, P, u, s, be, alB, beB, S = gen.tmpl(w)
    st = P + (u * be + s) * 36 + u * (alB * b + beB) + S
    tg = W([9] * ((12 * b + 8) // 5) + [8, 6] + [4] * ((24 * b + 186) // 5) + [1, 37, 18, 4])
    jobs.append(f'S0_b{b} {st} {len(st)} G {tg} G')
# (b) rules R1-R3 in the two real left contexts, random small parameters
random.seed(1)
for i in range(300):
    x = random.choice([0, 1, 4, 16])
    ctx = [9] * x + [8] + random.choice([[6], [0, random.choice([4, 7, 10, 13, 22])], [3]])
    L = [random.choice([1, 4, 7]) for _ in range(random.randint(0, 4))]
    r = 3 * random.randint(0, 8)
    kind = random.choice(['R1', 'R2', 'R3'])
    if kind == 'R1':
        m = random.choice([1, 4, 7, 10, 13]); add(f'R1_{i}', ctx + L + [1, m + 3, r, 4], ctx + L + [1, m, 2 * r + 6, 4])
    elif kind == 'R2':
        X = random.choice([1, 4, 7, 10]); add(f'R2_{i}', ctx + L + [X + 3, 1, r, 4], ctx + L + [X, 2 * r + 7, 0, 4])
    else:
        Y = random.choice([1, 4, 7, 10]); k = random.randint(1, 5)
        add(f'R3_{i}', ctx + L + [Y + 3] + [1] * k + [1, r, 4], ctx + L + [Y, 2 * r + 7] + [1] * (k - 1) + [1, 0, 4])
# R3 borrowing from the context's own D6 (-> D3) and from a large digit token (2R+4 -> 2R+1)
for x in (0, 4, 16):
    for k in (1, 2, 5, 9):
        for r in (0, 3, 9, 30):
            add(f'R3D6_x{x}k{k}r{r}', [9] * x + [8, 6] + [1] * k + [1, r, 4], [9] * x + [8, 3, 2 * r + 7] + [1] * (k - 1) + [1, 0, 4])
            for R in (0, 3, 21, 60):
                add(f'R3big_x{x}k{k}r{r}R{R}', [9] * x + [8, 0, 2 * R + 4] + [1] * k + [1, r, 4], [9] * x + [8, 0, 2 * R + 1, 2 * r + 7] + [1] * (k - 1) + [1, 0, 4])
# (c) stage 1: [.. D3, 1^m | 1 | r] -> [.. D0, 2r+4, 4^(m-2), 1 | 37 | 18]
for x in (0, 1, 4, 16, 40):
    for m in (2, 3, 4, 5, 6, 7, 8, 11, 19, 43, 67):
        for r in (0, 3, 6, 9, 12, 30, 63, 90):
            add(f'S1_x{x}m{m}r{r}', [9] * x + [8, 3] + [1] * m + [1, r, 4], [9] * x + [8, 0, 2 * r + 4] + [4] * (m - 2) + [1, 37, 18, 4])
Path('jobs_0LA.txt').write_text('\n'.join(jobs) + '\n')
r = subprocess.run(['./reach2.exe', M, 'jobs_0LA.txt', '200000000'], capture_output=True, text=True)
bad = [l for l in r.stdout.splitlines() if '\tREACHED\t' not in l]
print(len(jobs), 'jobs,', len(jobs) - len(bad), 'REACHED')
for l in bad[:40]: print('  ', l)
