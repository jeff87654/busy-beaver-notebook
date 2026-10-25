"""Literal checks of the three-cycle sibling 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA.
Configurations: tokens D(m) = (10)^m 1, then the tail (10)^4, head on the blank right of it, state F."""
import random, subprocess
from pathlib import Path
import gen
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA'
T = '10' * 4
def D(m): return '10' * m + '1'
def W(toks): return ''.join(D(t) for t in toks) + T
jobs, halts = [], []
def add(lab, s, t): a, b = W(s), W(t); jobs.append(f'{lab} {a} {len(a)} F {b} F')
q, P, u, s_, be, alB, beB, S = gen.tmpl(gen.C35['c35fh'][1])
for b in range(1, 200, 5):
    st = P + (u * be + s_) * 36 + u * (alB * b + beB) + S
    tg = W([9] * ((12 * b + 8) // 5) + [8, 6] + [4] * ((24 * b + 186) // 5) + [1, 37, 18])
    jobs.append(f'S0_b{b} {st} {len(st)} F {tg} F')
random.seed(2)
for i in range(300):
    x = random.choice([1, 4, 16])
    ctx = [9] * x + [8] + random.choice([[6], [0, random.choice([4, 7, 22])], [3], [random.choice([0, 3, 12, 42]), 0]])
    L = [random.choice([1, 4, 7]) for _ in range(random.randint(0, 4))]
    r = 3 * random.randint(0, 8); kind = random.choice(['R1', 'R2', 'R3'])
    if kind == 'R1':
        m = random.choice([1, 4, 7, 10, 13]); add(f'R1_{i}', ctx + L + [1, m + 3, r], ctx + L + [1, m, 2 * r + 6])
    elif kind == 'R2':
        X = random.choice([1, 4, 7, 10]); add(f'R2_{i}', ctx + L + [X + 3, 1, r], ctx + L + [X, 2 * r + 7, 0])
    else:
        Y = random.choice([1, 4, 7, 10]); k = random.randint(1, 5)
        add(f'R3_{i}', ctx + L + [Y + 3] + [1] * k + [1, r], ctx + L + [Y, 2 * r + 7] + [1] * (k - 1) + [1, 0])
for x in (1, 4, 16):
    for k in (1, 2, 5):
        for r in (0, 9, 30):
            add(f'R3D6_x{x}k{k}r{r}', [9] * x + [8, 6] + [1] * k + [1, r], [9] * x + [8, 3, 2 * r + 7] + [1] * (k - 1) + [1, 0])
            for R in (0, 3, 21, 60):
                add(f'R3big_x{x}k{k}r{r}R{R}', [9] * x + [8, 0, 2 * R + 4] + [1] * k + [1, r], [9] * x + [8, 0, 2 * R + 1, 2 * r + 7] + [1] * (k - 1) + [1, 0])
for x in (2, 4, 16, 40):
    for m in (2, 3, 4, 5, 7, 11, 43, 67):
        for r in (0, 3, 9, 30, 63, 90):
            add(f'S1_x{x}m{m}r{r}', [9] * x + [8, 3] + [1] * m + [1, r], [9] * x + [8, 0, 2 * r + 4] + [4] * (m - 2) + [1, 37, 18])
            if r >= 9:
                add(f'S2_x{x}m{m}r{r}', [9] * x + [8, 0] + [1] * m + [1, r], [9] * (x - 2) + [8, 2 * r - 18, 0] + [4] * (m + 40) + [1, 37, 18])
Path('jobs_fh.txt').write_text('\n'.join(jobs) + '\n')
out = subprocess.run(['./reach2.exe', M, 'jobs_fh.txt', '300000000'], capture_output=True, text=True).stdout.splitlines()
bad = [l for l in out if '\tREACHED\t' not in l]
print(len(jobs), 'jobs,', len(jobs) - len(bad), 'REACHED')
for l in bad[:30]: print('  ', l)
