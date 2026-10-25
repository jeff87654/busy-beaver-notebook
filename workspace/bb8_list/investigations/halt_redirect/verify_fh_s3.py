import subprocess
from pathlib import Path
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA'
T = '10' * 4
def D(m): return '10' * m + '1'
def W(t): return ''.join(D(x) for x in t) + T
jobs, meta = [], {}
# grid: [D9^y, D8, D(s), D0, D1^n | D1 | D(r)]
for y in (0, 3, 7):
    for s in (0, 6, 18, 60):
        for n in list(range(0, 30)) + [43, 67, 91]:
            for r in (0, 3, 6, 9, 12, 48, 123):
                lab = f'y{y}s{s}n{n}r{r}'; w = W([9] * y + [8, s, 0] + [1] * n + [1, r])
                jobs.append(f'{lab} {w} {len(w)} F 1 F'); meta[lab] = (y, s, n, r)
# real-class representatives for the ones formula
for b in (16, 41, 66):
    for R2 in (9, 30, 99):
        for R3 in (48, 123, 198):
            y, n, s = (12 * b - 2) // 5, (24 * b + 396) // 5, 2 * R2 - 18
            lab = f'b{b}R2{R2}R3{R3}'; w = W([9] * y + [8, s, 0] + [1] * n + [1, R3])
            jobs.append(f'{lab} {w} {len(w)} F 1 F'); meta[lab] = (b, R2, R3)
Path('jobs_fh_s3.txt').write_text('\n'.join(jobs) + '\n')
out = subprocess.run(['./reach2.exe', M, 'jobs_fh_s3.txt', '300000000'], capture_output=True, text=True).stdout.splitlines()
pat = {}
for l in out:
    f = l.split('\t')
    if not f[0].startswith('y'): continue
    y, s, n, r = meta[f[0]]
    k = 'H-' + f[3] + f[4] if f[1] == 'HALT' else f[1]
    pat.setdefault(k, []).append((y, s, n, r))
for k, v in pat.items():
    print(k, len(v))
    if k != 'H-I0':
        print('   n values:', sorted({x[2] for x in v}), ' r values:', sorted({x[3] for x in v}), ' s values:', sorted({x[1] for x in v}))
ok = tot = 0
for l in out:
    f = l.split('\t')
    if not f[0].startswith('b'): continue
    b, R2, R3 = meta[f[0]]; tot += 1
    num = 25 * 2 * R2 + 65 * R3 + 816 * b + 4224
    pred = num // 25 if num % 25 == 0 else None
    if f[1] == 'HALT' and f[3] == 'I' and f[4] == '0' and pred is not None and int(f[5]) == pred: ok += 1
    else: print('MISMATCH', l, pred)
print(f'ones = 2R2 + 13R3/5 + (816b+4224)/25 in the real class: {ok}/{tot}')
