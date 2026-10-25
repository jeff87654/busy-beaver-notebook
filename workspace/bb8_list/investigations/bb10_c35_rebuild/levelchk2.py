"""Omega-level screen for halters after full cycles (mode A rows from mf_batch output):
rerun in mode F (every accumulator created after the start represented by b = 126 instead of b = 6).
A crossed length that changes (same stage index) or a longer run of stages means some crossed run or loop count
depends on a post-start accumulator.  The row is flagged DEP if that happens after the first big jump (so the
accumulator involved is itself omega-level >= 1): a candidate for omega-level 2.
python levelchk2.py MACHINES.txt MFOUT.tsv OUT.tsv"""
import sys
from concurrent.futures import ThreadPoolExecutor
import mf35
ms = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
hist = {}
for l in open(sys.argv[2]):
    f = l.rstrip('\n').split('\t')
    if len(f) >= 5:
        hist[f[0]] = f[4].split(' ; ')
done = set()
try:
    done = set(l.split('\t')[0] for l in open(sys.argv[3]))
except FileNotFoundError:
    pass
ms = [m for m in ms if m not in done and m in hist]
print(len(ms), 'machines', flush=True)
def job(m):
    za = [mf35.zeros_of(x) for x in hist[m] if x.startswith('J')]
    k, h = mf35.follow(m, 'F', 300, 300_000_000)
    zf = [mf35.zeros_of(x) for x in h if x.startswith('J')]
    first_big = next((i for i, z in enumerate(za) if z is not None and z >= 50), None)
    diff = next((i for i, (x, y) in enumerate(zip(za, zf)) if x != y), None)
    if diff is None and len(za) != len(zf):
        diff = min(len(za), len(zf))
    tag = 'same'
    if diff is not None:
        tag = 'DEP' if first_big is not None and diff > first_big else 'dep-early'
    return m, k, len(h), tag, first_big, diff, max([z for z in za if z is not None] or [0]), max([z for z in zf if z is not None] or [0])
with ThreadPoolExecutor(2) as ex, open(sys.argv[3], 'a') as f:
    for r in ex.map(job, ms):
        f.write('\t'.join(str(x) for x in r) + '\n'); f.flush()
        print(*r, flush=True)
