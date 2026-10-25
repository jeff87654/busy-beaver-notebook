"""For mini-follower HALT results with big jumps: rerun in mode F (later accumulators represented by b = 126 instead of
b = 6) and mode C (start b = 126).  A jump whose zero count changes between A and F crossed a run whose length depends
on a later (already omega-level) accumulator: omega-level >= 2.  python levelchk.py IN.tsv OUT.tsv"""
import sys
from concurrent.futures import ThreadPoolExecutor
import mf35
src, dst = sys.argv[1], sys.argv[2]
rows = []
for l in open(src):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 5 and f[1] == 'HALT' and mf35.big_jumps(f[4].split(' ; '), 50) > 0:
        rows.append(f[0])
done = set()
try:
    done = set(l.split('\t')[0] for l in open(dst))
except FileNotFoundError:
    pass
rows = [m for m in dict.fromkeys(rows) if m not in done]
print(len(rows), 'machines', flush=True)
def job(m):
    out = [m]
    za = None
    for mode in 'AFC':
        k, h = mf35.follow(m, mode, 300, 300_000_000)
        zs = [mf35.zeros_of(x) for x in h if x.startswith('J')]
        out += [mode + ':' + k, str(len(h)), ','.join(str(z) for z in zs[:60])]
    return out
with ThreadPoolExecutor(2) as ex, open(dst, 'a') as f:
    for r in ex.map(job, rows):
        a, fz = r[3], r[6]
        lvl2 = 'LEVEL2?' if a != fz else 'level1'
        f.write('\t'.join(r + [lvl2]) + '\n'); f.flush()
        print(r[0], r[1], r[4], r[7], lvl2, flush=True)
