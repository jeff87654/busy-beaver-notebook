# check_c7_rest.py: Faithful w150 + --cnt screen of:
# 1. Reachable non-HALT rows of br2_out.tsv
# 2. Reachable LOOP / MAXSTAGES / HALT(nst>=2) rows of mf_out.tsv
# 3. Children (and grandchildren if nu>=2) of multi-undef HALT rows in c7_multi_w150_cnt.tsv and br2_out.tsv
import subprocess, os, sys, re, concurrent.futures
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_resid\tools')
import backref_s

EXE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_y1_fable\tools\pkf8.exe'
OUT_TSV = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_rest_w150_cnt.tsv'
LOW = getattr(subprocess, 'IDLE_PRIORITY_CLASS', 0)

SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1']
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHI']

def setslot(m, slot, val):
    i = SL.index(slot); q, c = divmod(i, 2)
    parts = m.split('_'); s = parts[q]
    parts[q] = s[:3 * c] + val + s[3 * c + 3:]
    return '_'.join(parts)

def is_reachable(m):
    res = backref_s.check(m, depth=20, maxnodes=50000)
    return any('POSSIBLE' in v or 'UNDECIDED' in v for _, v in res)

def expand_halt_slot(m, slot):
    out = []
    if slot not in SL: return out
    i = SL.index(slot); q, c = divmod(i, 2)
    if m.split('_')[q][3 * c:3 * c + 3] != '---':
        return out
    for opt in OPTS:
        # If state I is completely unused so far, TNF-canonicalize by only allowing I in {0LI,0RI,1LI,1RI}
        if m.endswith('_------') and 'I' not in m[:-7]:
            pass
        cm = setslot(m, slot, opt)
        if cm.count('---') >= 1 and is_reachable(cm):
            out.append(cm)
    return out

seen = set()
for fn in [
    r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_1undef_w150_cnt.tsv',
    r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_multi_w150_cnt.tsv',
]:
    if os.path.exists(fn):
        for l in open(fn):
            seen.add(l.split('\t')[0])

if os.path.exists(OUT_TSV):
    for l in open(OUT_TSV):
        seen.add(l.split('\t')[0])

todo = []
def add_cand(m):
    if m not in seen:
        seen.add(m)
        todo.append(m)

# 1. br2_out.tsv non-HALT reachable + children of multi-undef HALT
for l in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7\br2_out.tsv'):
    if '\t' not in l: continue
    f = l.rstrip('\n').split('\t')
    m, k = f[0], f[1]
    if k != 'HALT':
        if is_reachable(m):
            add_cand(m)
    elif m.count('---') >= 2:
        mm = re.search(r'H ([HI][01])', f[4])
        if mm:
            for cm in expand_halt_slot(m, mm.group(1)):
                add_cand(cm)

# 2. Children of multi-undef HALT in c7_multi_w150_cnt.tsv (excluding M8 = 1LH/1RG which is F1)
for l in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_redir\runs\c7_multi_w150_cnt.tsv'):
    if '\t' not in l: continue
    m, v, nj, zs = l.rstrip('\n').split('\t')
    if v.startswith('HALT') and m != '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_1RG---_------':
        slot = v.split()[1]
        for cm in expand_halt_slot(m, slot):
            add_cand(cm)

# 3. mf_out.tsv LOOP / MAXSTAGES / HALT(nst>=2)
for l in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7\mf_out.tsv'):
    if '\t' not in l: continue
    f = l.rstrip('\n').split('\t')
    m, k, nst = f[0], f[1], int(f[2])
    if k in ('LOOP', 'MAXSTAGES') or (k == 'HALT' and nst >= 2):
        if is_reachable(m):
            add_cand(m)

print(f'Initial queue: {len(todo)} machines', flush=True)

def run_one(m):
    cmd = [EXE, m, '--B', '66', '--rk', '0.1', '--rc', '10', '--cls', '66', '--mod', '150', '--cnt', '--jumps', '150', '--maxs', '5e7', '--maxt', '5e8', '--rcap', '500000', '--quiet']
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

os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
with open(OUT_TSV, 'a') as fo:
    level = 0
    while todo and level < 3:
        level += 1
        print(f'=== Pass {level}: {len(todo)} machines ===', flush=True)
        nxt = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            for m, verdict, nj, zeros in ex.map(run_one, todo):
                fo.write(f'{m}\t{verdict}\t{nj}\t{zeros}\n')
                fo.flush()
                zs = [int(x) for x in zeros.split()]
                big_zs = [z for z in zs if z >= 50]
                if verdict.startswith('HALT'):
                    if len(big_zs) >= 2 and not (len(big_zs) == 7 and big_zs[0] == 817):
                        print(f'HALT-HIT (L{level}): {m} | {verdict} | nj={nj} | zeros={zeros[:100]}', flush=True)
                    if m.count('---') >= 2 and nj >= 2:
                        slot = verdict.split()[1]
                        for cm in expand_halt_slot(m, slot):
                            if cm not in seen:
                                seen.add(cm)
                                nxt.append(cm)
                else:
                    if len(set(big_zs)) >= 4:
                        print(f'ESC-HIT (L{level}): {m} | {verdict} | nj={nj} | zeros={zeros[:100]}', flush=True)
        todo = nxt
print('ALL DONE', flush=True)
