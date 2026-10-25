# rescan_830_groups.py: Re-test all 830 distinct (verdict_type, nj, zeros) groups from C7
# using the patched pkf8.exe (--rk rounded to --cls 66 --mod 150, --jumps 250).
import subprocess, os, sys, re, concurrent.futures

EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_y1_fable\tools\pkf8.exe'
OUT_TSV = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_830groups_fixed.tsv'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)

def is_f1_twin(m):
    p = m.split('_')
    e0 = p[4][:3]; h0 = p[7][:3]; h1 = p[7][3:6]
    if e0 == '0LH' and h0 in ('0RC', '1RD') and h1.endswith('I'): return True
    if e0 == '1LH' and h0 in ('0RB', '0RE', '1RG') and h1.endswith('I'): return True
    if e0 == '0RH' and h1 == '1LC' and h0.endswith('I'): return True
    if e0 == '1RH' and h1 in ('0LF', '1LB', '1LE', '1RF') and h0.endswith('I'): return True
    return False

rows = {}
for fn in [
    r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_1undef_w150_cnt.tsv',
    r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_multi_w150_cnt.tsv',
    r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_rest_w150_cnt.tsv',
]:
    for l in open(fn):
        if '\t' not in l: continue
        f = l.rstrip('\n').split('\t')
        rows[f[0]] = (f[1], int(f[2]), f[3])

groups = {}
for m, (v, nj, zs) in rows.items():
    if is_f1_twin(m): continue
    if nj < 2: continue
    key = (v.split()[0], nj, zs)
    groups.setdefault(key, []).append(m)

reps = [ms[0] for ms in groups.values()]
print(f'Testing {len(reps)} group representatives...', flush=True)

def run_one(m):
    cmd = [EXE, m, '--B', '66', '--rk', '0.02', '--rc', '10', '--cls', '66', '--mod', '150', '--cnt', '--jumps', '250', '--maxs', '5e7', '--maxt', '5e8', '--rcap', '500000', '--quiet']
    p = subprocess.run(cmd, capture_output=True, text=True, creationflags=LOW)
    out = p.stdout
    verdict = 'OTHER'
    zeros = ''
    nj = 0
    for l in out.splitlines():
        if l.startswith(('HALT', 'STOP', 'END', 'RCAP')):
            verdict = l.strip()
        elif l.startswith('zeros:'):
            zeros = l[6:].strip()
            nj = len(zeros.split())
    return (m, verdict, nj, zeros)

with open(OUT_TSV, 'w') as fo:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for m, verdict, nj, zeros in ex.map(run_one, reps):
            fo.write(f'{m}\t{verdict}\t{nj}\t{zeros}\n')
            fo.flush()
            zs = [int(x) for x in zeros.split()]
            big_zs = [z for z in zs if z >= 50]
            if verdict.startswith('HALT'):
                if len(big_zs) >= 2 or nj >= 15:
                    print(f'HALT-HIT: {m} | {verdict} | nj={nj} | zeros={zeros[:110]}', flush=True)
            else:
                if len(set(big_zs)) >= 4 or (nj >= 30 and max(zs or [0]) >= 50):
                    print(f'ESC-HIT: {m} | {verdict} | nj={nj} | zeros={zeros[:110]}', flush=True)
print('DONE 830 GROUPS', flush=True)
