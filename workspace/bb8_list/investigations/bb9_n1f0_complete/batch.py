"""batch.py: run zfg.exe (generic zeroing follower, real blank-tape start) on every row of ROWS.tsv for several
accumulator representatives R (R0 = R), 2 Idle workers.  Appends to OUT.tsv (rows/R already present are skipped):
  machine grade template undefined R outcome nj zeros(RLE of cleared-list lengths) used undefined_read
outcome: H<slot>@J<n> (slot read; an undefined slot = halt), T@J<n> (segment budget), J<n> (jump limit).
  python batch.py ROWS.tsv OUT.tsv [--R 18-29] [--jumps 3000] [--maxs 1e9] [--logdir logs]"""
import sys, argparse, subprocess, os, re
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('rows'); ap.add_argument('out'); ap.add_argument('--R', default='18-29'); ap.add_argument('--R0', default=None)
ap.add_argument('--jumps', type=int, default=3000); ap.add_argument('--maxs', default='3e8'); ap.add_argument('--logdir', default='logs')
ap.add_argument('--workers', type=int, default=2); ap.add_argument('--maxtotal', default='2e9')
a = ap.parse_args()
def rng(s):
    out = []
    for p in s.split(','):
        if '-' in p:
            x, y = p.split('-'); out += list(range(int(x), int(y) + 1))
        else:
            out.append(int(p))
    return out
Rs = rng(a.R)
rows = [l.rstrip('\n').split('\t') for l in open(a.rows) if l.strip()]
done = set()
if os.path.exists(a.out):
    for l in open(a.out):
        x = l.split('\t'); done.add((x[0], x[4], x[5] if len(x) > 5 else ''))
os.makedirs(os.path.join(HERE, a.logdir), exist_ok=True)
jobs = []
for i, r in enumerate(rows):
    for R in Rs:
        R0 = R if a.R0 is None else int(a.R0)
        key = (r[0], str(R0), str(R))
        if key not in done:
            jobs.append((r, R0, R))
def one(job):
    r, R0, R = job
    m, g, t = r[0], r[1], r[2]
    und = r[4] if len(r) > 4 else '-'
    lg = os.path.join(HERE, a.logdir, f'{m}_R0{R0}_R{R}.log')
    with open(lg, 'w') as f:
        subprocess.call([os.path.join(HERE, 'zfg.exe'), m, t, '--R0', str(R0), '--R', str(R), '--jumps', str(a.jumps),
                         '--maxs', a.maxs, '--maxtotal', a.maxtotal, '--far', '120'], stdout=f, creationflags=0x40)
    leaf = [l for l in open(lg) if l.startswith('LEAF')]
    if not leaf:
        res = ['CRASH', '', '', '', '']
    else:
        L = leaf[-1]
        mm = re.search(r'LEAF \S+ (.*?) zeros=\[(.*?)\] used=(\S*)', L)
        head, zz, used = mm.group(1), mm.group(2), mm.group(3)
        if head.startswith('H '):
            h = re.match(r'H (\S+) @J(\d+)', head); outc = f'H{h.group(1)}@J{h.group(2)}'; nj = h.group(2)
            ur = h.group(1) if h.group(1) in und.split(',') else '-'
        elif head.startswith('T '):
            h = re.match(r'T @J(\d+)', head); outc = f'T@J{h.group(1)}'; nj = h.group(1); ur = '-'
        else:
            nj = head[1:]; outc = f'J{nj}'; ur = '-'
        res = [outc, nj, zz, used, ur]
    return [m, g, t, und, str(R0), str(R)] + res
with ThreadPoolExecutor(a.workers) as ex, open(a.out, 'a') as fo:
    for res in ex.map(one, jobs):
        fo.write('\t'.join(res) + '\n'); fo.flush()
        print('\t'.join(res[:2] + res[4:8] + [res[8][:100]] + res[10:]), flush=True)
