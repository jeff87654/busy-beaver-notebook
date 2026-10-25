"""collect6.py: merge deep6 outputs -> final6.tsv (one row per machine with any signal) + summary on stdout."""
import glob, os, collections
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def rows(pat):
    for p in sorted(glob.glob(pat)):
        for l in open(p):
            if not l.startswith(('#', 'machine')): yield l.rstrip('\n').split('\t')
def fl(x):
    try: return float(x)
    except ValueError: return 0.0
ctl = [l.split()[0] for l in open('ctl6.txt')]
pool = [l.split()[0] for l in open('pool.txt')]
dl2 = {f[0]: f for f in rows('dl2/p*.tsv')}
dl = {f[0]: f for f in rows('dl/p*.tsv')}
full = {f[0]: f for f in rows('full/p*.tsv') if len(f) >= 17}
pil = {f[0]: f for f in rows('pil/p*.tsv')}
small = collections.defaultdict(str)
for d in ('small', 'small20'):
    for p in glob.glob(f'{d}/K*.tsv'):
        k = p.split('K')[-1].split('.')[0]
        for f in rows(p):
            if f[2] == 'HALT': small[f[0]] += f'{d}:K{k} '
life = {}
for p in glob.glob('life/K*.tsv'):
    k = p.split('K')[-1].split('.')[0]
    for f in rows(p):
        d = int(f[2]) if fl(f[3]) >= 0.5 else 0
        if d > life.get(f[0], (0, ''))[0] or f[0] not in life: life[f[0]] = (d, k)
ht = {}
for p in glob.glob('ht/K*.tsv'):
    k = p.split('K')[-1].split('.')[0]
    for f in rows(p):
        if len(f) >= 9 and int(f[7]) >= ht.get(f[0], (-1, ''))[0]: ht[f[0]] = (int(f[7]), f'K{k}:{f[8]}' + (' HALT' if f[2] == 'HALT' else ''))
cnt = collections.Counter()
out = []
for m in pool:
    g = dl2.get(m, ['', '', '0', '?'])
    ntpl = int(g[2]) if g[2].isdigit() else 0; grade = g[3] if len(g) > 3 else '?'
    k = dl.get(m); full_keys = k[3] if k and len(k) > 3 else ''
    f = full.get(m); fr = int(f[16]) if f else 0; srs = int(f[6]) if f else 0
    nat = f[2] if f else '?'; natlg = fl(f[3]) if f else 0; k2lg = fl(f[11]) if f else 0
    d, dk = life.get(m, (0, '-')); sm = small.get(m, '').strip(); h = ht.get(m, (-1, '-'))
    cnt['rows'] += 1; cnt['templated(dl2 n_templates>0)'] += ntpl > 0; cnt['dl2 graded'] += grade not in ('-', '?', '')
    cnt['dlscan full keys'] += bool(full_keys and full_keys not in ('-', '0'))
    cnt['natural HALT'] += nat == 'HALT'; cnt['FR>0'] += fr > 0; cnt['SRs>=10'] += srs >= 10
    cnt['small-probe HALT'] += bool(sm); cnt['D>=4'] += d >= 4
    tier = 1 if fr > 0 and d >= 4 else 2 if fr > 0 and sm else 3 if fr > 0 else 4 if sm and d >= 4 else 5 if (sm or d >= 4 or srs >= 10 or nat == 'HALT' or grade not in ('-', '?', '')) else 9
    if tier == 9 and m not in ctl: continue
    out.append((tier, -d, -fr, -srs, m, 'CTL' if m in ctl else '', grade, ntpl, full_keys, nat, f'{natlg:.2f}', f'{k2lg:.2f}', fr, srs, d, dk, sm or '-', h[0], h[1], (f[17][:120] if f and len(f) > 17 else '')))
out.sort()
with open('final6.tsv', 'w') as o:
    o.write('tier\tmachine\tctl\tdl2grade\tntpl\tdl_full\tnat\tnat_lg\tk2_lg\tFR\tSRs\tD\tDK\tsmallHALT\tHT\tHTiv\tshape\n')
    for x in out: o.write('\t'.join(map(str, (x[0],) + x[4:])) + '\n')
for k, v in cnt.items(): print(f'{k}: {v}')
print('tiers', collections.Counter(x[0] for x in out))
