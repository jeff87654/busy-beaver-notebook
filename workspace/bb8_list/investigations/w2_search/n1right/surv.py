"""surv.py LOG MACHINE STAGES [R] [L]: right-end survival classification.
For each J config (stage in STAGES, r := R) and every pattern P (bit strings starting with 1 of length <= L, plus
unary-token patterns 1^d (0 1^d)*), gap g in 1..8 and g = bmax+1 (just beyond the stage's own reach):
  U untouched (never read in the stage) | E erased (tokens = base, nothing right) | S preserved/shifted (tokens = base,
  bits remain right) | Mr merged into a/r only | Md merged into digits | X tokens differ and bits remain | H/T/W.
Prints class counts per stage, the first-divergence contexts, and samples."""
import sys, itertools, collections
from rlib import twin, word, rle
from logcfg import configs
log, M, stages = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(',')]
R = int(sys.argv[4]) if len(sys.argv) > 4 else 19
L = int(sys.argv[5]) if len(sys.argv) > 5 else 8
pats = ['1' + ''.join(b) for n in range(1, L + 1) for b in itertools.product('01', repeat=n - 1)]
tokp = []
for d in range(1, 7):
    for c in range(1, 4):
        tokp.append('0'.join(['1' * d] * c))
pats += [p for p in tokp if p not in pats]
cf = {s: (t, f) for s, t, f, _, _ in configs(log)}
for s in stages:
    toks, far = cf[s]; toks = toks[:-1] + [R]; w = word(toks, far)
    base = twin(M, w, 10**6, '-', maxs=3 * 10**9)
    bmax = base['bmax']; bt = base['base']
    print(f'== stage {s} R={R} base: {bt.get("desc", bt)} bmax={bmax} koff={bt.get("off")}', flush=True)
    cnt = collections.Counter(); ctx = collections.Counter(); samp = collections.defaultdict(list)
    for g in list(range(1, 9)) + [bmax + 1]:
        for p in pats:
            r = twin(M, w, g, p, maxs=20 * bt.get("steps", 10**6) + 10**6)
            pt = r['pat']
            if r['read'] == '-': c = 'U'
            elif pt['kind'] != 'K': c = pt['kind']
            elif pt['toks'] == bt['toks'] and pt['far'] == bt['far']:
                c = 'E' if pt['rem'] == '-' else 'S'
            elif pt['rem'] == '-':
                c = 'Mr' if pt['toks'][2:] == bt['toks'][2:] and pt['far'] == bt['far'] else 'Md'
            else: c = 'X'
            gg = 'far' if g == bmax + 1 else 'near'
            cnt[(gg, c)] += 1
            if r['div'] != '-': ctx[r['div'].split()[1]] += 1
            if len(samp[c]) < 4: samp[c].append((p, g, pt.get('desc', pt.get('raw')), pt.get('rem'), pt.get('off'), r['div']))
    print('  counts', dict(sorted(cnt.items())))
    print('  first-divergence contexts', dict(ctx.most_common()))
    for c, v in samp.items():
        for x in v: print('   ', c, x)
