"""post.py TSV.. --out OUT: for every enumeration leaf with >= 1 RSIG (std), re-run under the big policy (k=17) to the
first RSIG and under std at k = 29, 41: prints machine, std RSIGs, big c (accumulator-sized if >> std c), minlo
(in place if >= -8), k-test results.  Leaves are deduplicated by machine string."""
import sys, threading, argparse
from ilib import stage, rsig, far_of, word_of, SUF
ap = argparse.ArgumentParser(); ap.add_argument('tsv', nargs='+'); ap.add_argument('--out', required=True)
ap.add_argument('--S', type=int, default=40); ap.add_argument("--minrs", type=int, default=1); ap.add_argument("--bigmaxs", type=int, default=3 * 10**8); ap.add_argument('--bysig', action='store_true'); ap.add_argument('--n', type=int, default=41)
a = ap.parse_args()
def first_rs(M, k, pol, S):
    word = far_of(k) + word_of([0] + [1] * a.n + [1, 19]) + SUF
    A = 0; lo = 0
    for st in range(S):
        kind, d = stage(M, word, a.bigmaxs if pol == "big" else 10**8, pol)
        if d.get('LO') is not None: lo = min(lo, A + d['LO'])
        if kind != 'K': return f'{kind}{d.get("slot","")}@{st}', lo
        r = rsig(d['toks'])
        if r and st > 0: return f'RS@{st}:P{len(r[0])}:c{r[1]}:z{r[2]}', lo
        A += d['shift']; word = d['newword']
    return 'none', lo
def go():
    seen = set(); fo = open(a.out, 'w')
    for fn in a.tsv:
        for line in open(fn):
            f = line.rstrip('\n').split('\t')
            key = f[4] if a.bysig else f[0]
            if len(f) < 5 or int(f[3]) < a.minrs or key in seen: continue
            seen.add(key); M = f[0]
            b, lob = first_rs(M, 17, 'big', a.S)
            k29, _ = first_rs(M, 29, 'std', a.S); k41, _ = first_rs(M, 41, 'std', a.S)
            row = f'{M}\t{f[1]}\t{f[4]}\tbig={b}\tminlo_big={lob}\tk29={k29}\tk41={k41}'
            print(row, flush=True); fo.write(row + '\n'); fo.flush()
sys.setrecursionlimit(300000); threading.stack_size(250 * 1024 * 1024)
t = threading.Thread(target=go); t.start(); t.join()
