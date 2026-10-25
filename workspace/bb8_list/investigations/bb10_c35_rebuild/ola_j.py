"""10-state extensions of the 9-state 0LA machine 1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_---0LA:
its halt slot I0 is redirected.  Only I0 -> J can make J reachable (every other slot is fixed), so I0 in
{0LJ, 0RJ, 1LJ, 1RJ}; then J0/J1 are branched TNF-style as the real run (mini-follower, b = 6 representatives) first
reads them, one of them staying undefined as the halt.
Every run is followed in mode A (all huge accumulators at b = 6) and, when it halts after stage 2, in mode F (all
accumulators created after the start at b = 126).  A big jump after the old halting point whose crossed length
changes between A and F crossed a run built from a post-first-cycle (omega-level >= 1) accumulator: omega-level >= 2.
python ola_j.py OUT.tsv [STAGES] [MAXS]"""
import sys, re
from concurrent.futures import ThreadPoolExecutor
import mf35
out = sys.argv[1]
ST = int(sys.argv[2]) if len(sys.argv) > 2 else 300
MS = int(sys.argv[3]) if len(sys.argv) > 3 else 20_000_000
BASE = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC0RH_1RG1LF_{I0}0LA_{J0}{J1}'
OPTS = [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in 'ABCDEFGHIJ']
def mk(i0, j0='---', j1='---'):
    return BASE.format(I0=i0, J0=j0, J1=j1)
def run(m):
    k, h = mf35.follow(m, 'A', ST, MS)
    zs = [mf35.zeros_of(x) for x in h if x.startswith('J')]
    res = {'m': m, 'kind': k, 'n': len(h), 'last': h[-1] if h else '', 'zA': zs}
    if k == 'HALT' and len(zs) > 2 and max(zs[2:] or [0]) >= 50:
        k2, h2 = mf35.follow(m, 'F', ST, 10 * MS)
        res['kindF'] = k2
        res['zF'] = [mf35.zeros_of(x) for x in h2 if x.startswith('J')]
    return res
def slot_of(last):
    mm = re.match(r'H (J)(\d)', last)
    return (mm.group(1) + mm.group(2)) if mm else None
rows = []
with ThreadPoolExecutor(3) as ex, open(out, 'w') as f:
    level = [mk(i0) for i0 in ('0LJ', '0RJ', '1LJ', '1RJ')]
    depth = 0
    while level:
        depth += 1
        nxt = []
        for r in ex.map(run, level):
            zA = r['zA']; post = zA[2:]
            lvl = ''
            if 'zF' in r:
                lvl = 'LEVEL2' if r['zF'][:len(zA)] != zA or len(r['zF']) != len(zA) else 'level1'
            f.write(f"{r['m']}\t{r['kind']}\t{r['n']}\t{r['last']}\tpost-zeros={post[:40]}\t{r.get('kindF','')}\t"
                    f"{r.get('zF', [])[2:42] if 'zF' in r else ''}\t{lvl}\tD{depth}\n"); f.flush()
            print(r['m'], r['kind'], r['n'], r['last'], 'post', post[:12], lvl, flush=True)
            s = slot_of(r['last'])
            m = r['m']
            if r['kind'] == 'HALT' and s and m.count('---') >= 2:
                # branch this J slot (the other one stays undefined = the halt)
                j0, j1 = m[-6:-3], m[-3:]
                for v in OPTS:
                    nxt.append(m[:-6] + (v + j1 if s == 'J0' else j0 + v))
        level = nxt
print('done', flush=True)
