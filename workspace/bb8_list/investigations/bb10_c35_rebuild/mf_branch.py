"""Second-level TNF branching: for every mini-follower result HALT (an undefined slot read at some stage), try all 40
values of that slot and follow the children; recurse while children halt at further undefined slots.
python mf_branch.py IN.tsv OUT.tsv WORKERS [STAGES=10] [MAXS=500000] [MINSTAGE=1]
IN rows: machine kind nstages bigjumps history (mf_batch format).  Only HALT rows whose halt stage >= MINSTAGE
(stage index = number of jumps before the halt) are branched."""
import sys, re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mf35
src, out, W = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
ST = int(sys.argv[4]) if len(sys.argv) > 4 else 10
MS = int(sys.argv[5]) if len(sys.argv) > 5 else 500000
MINST = int(sys.argv[6]) if len(sys.argv) > 6 else 1
SL = ['A0','A1','B0','B1','C0','C1','D0','D1','E0','E1','F0','F1','G0','G1','H0','H1','I0','I1','J0','J1']
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHIJ']
def setslot(m, slot, val):
    i = SL.index(slot); q, c = divmod(i, 2)
    parts = m.split('_'); s = parts[q]
    parts[q] = s[:3 * c] + val + s[3 * c + 3:]
    return '_'.join(parts)
def halt_slot(hist):
    h = hist.split(' ; ')[-1]
    mm = re.match(r'H (\w)(\d)', h)
    return (mm.group(1) + mm.group(2)) if mm else None
done = set(l.split('\t')[0] for l in out.read_text().splitlines() if l.strip()) if out.exists() else set()
todo = []
for l in open(src):
    f = l.rstrip('\n').split('\t')
    if len(f) < 5 or f[1] != 'HALT':
        continue
    nj = int(f[2]) - 1
    if nj < MINST:
        continue
    s = halt_slot(f[4])
    if s and s[0] in 'IJ':
        todo.append((f[0], s))
print(len(todo), 'halting parents', flush=True)
def job(m):
    try:
        kind, hist = mf35.follow(m, 'A', ST, MS)
    except Exception as ex:
        kind, hist = 'CRASH', [repr(ex)[:200]]
    return m, kind, len(hist), mf35.big_jumps(hist), ' ; '.join(hist)
with ThreadPoolExecutor(W) as ex, out.open('a') as f:
    level = 0
    while todo:
        level += 1
        kids = [setslot(m, s, v) for m, s in todo for v in OPTS]
        kids = [k for k in kids if k not in done]
        print('level', level, len(kids), 'children', flush=True)
        nxt = []
        for r in ex.map(job, kids):
            f.write('\t'.join(str(x) for x in r) + f'\tL{level}\n'); f.flush()
            done.add(r[0])
            if r[1] == 'HALT' and r[2] - 1 >= MINST:
                s = halt_slot(r[4])
                if s and s[0] in 'IJ':
                    nxt.append((r[0], s))
        todo = nxt
print('done', flush=True)
