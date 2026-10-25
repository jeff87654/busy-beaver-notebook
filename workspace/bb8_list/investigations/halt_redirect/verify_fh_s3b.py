import subprocess
from pathlib import Path
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA'
T = '10' * 4
def D(m): return '10' * m + '1'
def W(t): return ''.join(D(x) for x in t) + T
R = 49612750485498; B = 16537583495166
Rr = sorted({R % 1200, R % 1200 + 1200, R % 3600, R % 10800})
Br = sorted({B % 400, B % 2800, B % 400 + 400})
print('R reps', Rr, 'B reps', Br)
jobs, meta = [], {}
for b in Br:
    for R2 in Rr:
        for R3 in Rr[:3]:
            y, n, s = (12 * b - 2) // 5, (24 * b + 396) // 5, 2 * R2 - 18
            lab = f'b{b}R2{R2}R3{R3}'; w = W([9] * y + [8, s, 0] + [1] * n + [1, R3])
            jobs.append(f'{lab} {w} {len(w)} F 1 F'); meta[lab] = (b, R2, R3)
Path('jobs_fh_s3b.txt').write_text('\n'.join(jobs) + '\n')
out = subprocess.run(['./reach2.exe', M, 'jobs_fh_s3b.txt', '3000000000'], capture_output=True, text=True).stdout.splitlines()
ok = 0
for l in out:
    f = l.split('\t'); b, R2, R3 = meta[f[0]]
    num = 50 * R2 + 65 * R3 + 816 * b + 4224
    pred = num // 25 if num % 25 == 0 else None
    good = f[1] == 'HALT' and f[3] == 'I' and f[4] == '0' and pred is not None and int(f[5]) == pred
    ok += good
    print(('OK  ' if good else 'BAD ') + l, 'pred', pred)
print(f'real-class stage 3: {ok}/{len(out)} halt in I0 with ones = 2R2 + 13R3/5 + (816b+4224)/25')
