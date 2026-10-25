"""post.py: post-pass on cands.tsv (run collect.py first). For every candidate family representative:
  --life  at K=2 and at the list K (SRK): D = SRL of the longest-lived super-run with life >= 0.5 (list depth proxy)
  --small at K=2, SRK and the pilot K: SMALL-HALT if any small instance halts
Writes final.tsv ranked: tier 1 = FR>0 and D>=4; tier 2 = FR>0 and SMALL-HALT; tier 3 = other FR; tier 4 = SR class
SMALL-HALT with D>=4; tier 5 = rest. Within a tier: D, then FR. Idle priority, W workers (default 2)."""
import idle  # noqa: F401
import os, subprocess, sys, collections
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, 'nlp7v.exe')
W = int(sys.argv[1]) if len(sys.argv) > 1 else 2
CIN = sys.argv[2] if len(sys.argv) > 2 else 'cands.tsv'
PDIR = sys.argv[3] if len(sys.argv) > 3 else 'post'
FOUT = sys.argv[4] if len(sys.argv) > 4 else 'final.tsv'
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, CIN)) if not l.startswith('class')]
D = os.path.join(HERE, PDIR); os.makedirs(D, exist_ok=True)
jobs = collections.defaultdict(set)
for r in rows:
    for k in {'2', r[7]}: jobs[('life', k)].add(r[1])
    for k in {'2', r[7], r[3]}: jobs[('small', k)].add(r[1])
def run(key):
    mode, k = key
    inp = os.path.join(D, f'{mode}_K{k}.txt'); out = os.path.join(D, f'{mode}_K{k}.tsv')
    old = set()
    if os.path.exists(out):
        old = {l.split('\t')[0] for l in open(out)}
    todo = sorted(jobs[key] - old)
    if not todo: return
    open(inp, 'w').write('\n'.join(todo) + '\n')
    tmp = out + '.part'
    p = subprocess.Popen([EXE, inp, tmp, '1000000' if mode == 'life' else '2000000', '--' + mode, f'--K={k}'], creationflags=0x40)
    open(os.path.join(HERE, 'pids.txt'), 'a').write(f'{p.pid}\tpost\tnlp7v.exe {mode} K{k}\n')
    p.wait()
    with open(out, 'a') as o:
        for l in open(tmp):
            if not l.startswith(('machine', '#')): o.write(l)
    os.remove(tmp)
with ThreadPoolExecutor(W) as ex: list(ex.map(run, sorted(jobs)))
life, small = {}, {}
for (mode, k) in jobs:
    for l in open(os.path.join(D, f'{mode}_K{k}.tsv')):
        f = l.rstrip('\n').split('\t')
        if mode == 'life':
            d = int(f[2]) if float(f[3]) >= 0.5 else 0
            if d > life.get(f[0], (0, ''))[0]: life[f[0]] = (d, k)
            life.setdefault(f[0], (0, k))
        else:
            if f[2] == 'HALT': small[f[0]] = 'SMALL-HALT'
            else: small.setdefault(f[0], 'NO-HALT')
# HT (list hierarchy) for FR families with D >= 4: small instance without list cut, 5M macro, K = 2 and SRK
htj = collections.defaultdict(set)
for r in rows:
    if int(r[11]) > 0 and life.get(r[1], (0, ''))[0] >= 4:
        for k in {'2', r[7]}: htj[k].add(r[1])
def runht(k):
    inp = os.path.join(D, f'ht_K{k}.txt'); out = os.path.join(D, f'ht_K{k}.tsv')
    old = {l.split('\t')[0] for l in open(out)} if os.path.exists(out) else set()
    todo = sorted(htj[k] - old)
    if not todo: return
    open(inp, 'w').write('\n'.join(todo) + '\n'); tmp = out + '.part'
    p = subprocess.Popen([EXE, inp, tmp, '5000000', '--small', '--nolist', f'--K={k}'], creationflags=0x40)
    open(os.path.join(HERE, 'pids.txt'), 'a').write(f'{p.pid}\tpost\tnlp7v.exe ht K{k}\n'); p.wait()
    with open(out, 'a') as o:
        for l in open(tmp):
            if not l.startswith(('machine', '#')): o.write(l)
    os.remove(tmp)
with ThreadPoolExecutor(W) as ex: list(ex.map(runht, sorted(htj)))
ht = {}
for k in htj:
    for l in open(os.path.join(D, f'ht_K{k}.tsv')):
        f = l.rstrip('\n').split('\t')
        if len(f) < 9: continue
        if int(f[7]) >= ht.get(f[0], (-1, ''))[0]: ht[f[0]] = (int(f[7]), f'K{k}:' + f[8] + (' HALT' if f[2] == 'HALT' else ''))
out = []
for r in rows:
    m = r[1]; d, dk = life.get(m, (0, '-')); sm = small.get(m, '?'); fr = int(r[11])
    tier = 1 if fr > 0 and d >= 4 else 2 if fr > 0 and sm == 'SMALL-HALT' else 3 if fr > 0 else 4 if sm == 'SMALL-HALT' and d >= 4 else 5
    h = ht.get(m, (-1, '-'))
    out.append((tier, -d, -fr, r[0], sm, m, r[2], str(d), dk, r[11], str(h[0]), h[1], r[6], r[3], r[4], r[12][:150]))
out.sort()
with open(os.path.join(HERE, FOUT), 'w') as o:
    o.write('tier\tclass\tsmall\tmachine\tfamily\tD\tDK\tFR\tHT\tHTiv\tSRs\tK\tnat_lg\tshape\n')
    for x in out: o.write('\t'.join([str(x[0])] + list(x[3:])) + '\n')
print(collections.Counter(x[0] for x in out))
