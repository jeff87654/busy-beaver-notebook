"""longrun.py TSV --minrs 2 [--S 600]: for every distinct leaf machine with >= minrs RSIGs and at least one undefined
slot, follow (std, far_17 + [0 1^41|1|19]) for S stages: RSIG sequence (stage:|P|:c mod 14:z), outcome, minlo.
Flags HALTn = halt after n RSIGs."""
import sys, threading, argparse
from ilib import stage, rsig, far_of, word_of, SUF
ap = argparse.ArgumentParser(); ap.add_argument('tsv', nargs='+'); ap.add_argument('--minrs', type=int, default=2)
ap.add_argument('--S', type=int, default=600); ap.add_argument('--out', required=True); ap.add_argument('--maxs', type=float, default=2e8)
ap.add_argument('--k', type=int, default=17); ap.add_argument('--needfree', type=int, default=1)
a = ap.parse_args()
def run(M):
    word = far_of(a.k) + word_of([0] + [1] * 41 + [1, 19]) + SUF
    A = 0; lo = 0; rs = []
    for st in range(a.S):
        kind, d = stage(M, word, int(a.maxs))
        if d.get('LO') is not None: lo = min(lo, A + d['LO'])
        if kind != 'K': return f'{kind}{d.get("slot","")}@{st}', rs, lo
        r = rsig(d['toks'])
        if r and st > 0 and (not rs or st - rs[-1][0] > 3): rs.append((st, len(r[0]), r[1], r[2]))
        A += d['shift']; word = d['newword']
    return 'MAX', rs, lo
def go():
    seen = set(); fo = open(a.out, 'w')
    for fn in a.tsv:
        for line in open(fn):
            f = line.rstrip('\n').split('\t')
            if len(f) < 5 or int(f[3]) < a.minrs or f[0] in seen: continue
            if a.needfree and '---' not in f[0].split('_', 10)[-1]: continue
            seen.add(f[0])
            out, rs, lo = run(f[0])
            tag = f'HALT{len(rs)}' if out.startswith('H') else out
            row = f'{f[0]}\t{tag}\t{out}\tnrs={len(rs)}\tminlo={lo}\t' + ' '.join(f'{s}:P{p}:c{c}/{c%14}:z{z}' for s, p, c, z in rs[:12])
            print(row, flush=True); fo.write(row + '\n'); fo.flush()
threading.stack_size(250 * 1024 * 1024); sys.setrecursionlimit(300000)
t = threading.Thread(target=go); t.start(); t.join()
