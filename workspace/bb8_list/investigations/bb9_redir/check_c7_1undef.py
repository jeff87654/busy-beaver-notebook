# check_c7_1undef.py: Run pkf8.exe in w150 + --cnt on the 1,473 1-undefined-slot TIME rows of halt_redirect/c7/mf_out.tsv
# whose undefined slot survives backref_s (depth 20). Includes f3_0RC and any other 2-state gadget machines missed by mf35g.
import subprocess, os, sys, concurrent.futures
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_resid\tools')
import backref_s

EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_y1_fable\tools\pkf8.exe'
MF_OUT = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7\mf_out.tsv'
OUT_TSV = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_1undef_w150_cnt.tsv'

rows = []
for ln in open(MF_OUT):
    if '\t' not in ln: continue
    m, k = ln.split('\t')[:2]
    if k == 'TIME' and m.count('---') == 1:
        res = backref_s.check(m, depth=20, maxnodes=50000)
        if any('POSSIBLE' in v or 'UNDECIDED' in v for _, v in res):
            rows.append(m)

print(f'Testing {len(rows)} reachable 1-undef TIME rows with --cnt...', flush=True)

def run_one(m):
    cmd = [EXE, m, '--B', '66', '--rk', '0.1', '--rc', '10', '--cls', '66', '--mod', '150', '--cnt', '--jumps', '150', '--maxs', '5e7', '--maxt', '5e8', '--rcap', '500000', '--quiet']
    p = subprocess.run(cmd, capture_output=True, text=True)
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

os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
with open(OUT_TSV, 'w') as fo:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for m, verdict, nj, zeros in ex.map(run_one, rows):
            fo.write(f'{m}\t{verdict}\t{nj}\t{zeros}\n')
            if nj >= 5 and verdict.startswith('HALT'):
                print(f'HIT: {m} | {verdict} | nj={nj} | zeros={zeros[:100]}', flush=True)
print('DONE', flush=True)
