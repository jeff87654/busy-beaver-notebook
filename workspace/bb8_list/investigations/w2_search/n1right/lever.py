"""lever.py LOG MACHINE STAGE [Rs] : merge-lever table at a restart stage.  For every short right pattern (length <= 4)
at gaps 1..2R+14, run the restart stage and report whether the K-moment is still a clean round start
'2 5 1^m 0^3 9 1^n' and its counter m (base: m = 4R+3).  Prints the distinct outcomes with the (pattern, gap) lists."""
import sys, itertools, collections, re
from rlib import twin, word, rle
from logcfg import configs
log, M, st = sys.argv[1], sys.argv[2], int(sys.argv[3])
Rs = [int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else '19,79').split(',')]
pats = ['1' + ''.join(b) for n in range(1, 5) for b in itertools.product('01', repeat=n - 1)]
cf = {s: (t, f) for s, t, f, _, _ in configs(log)}
for R in Rs:
    toks, far = cf[st]; toks = toks[:-1] + [R]; w = word(toks, far)
    base = twin(M, w, 10**6, '-', maxs=3 * 10**9); bt = base['base']
    print(f'== stage {st} R={R}: base {bt.get("desc")} bmax={base["bmax"]}', flush=True)
    out = collections.defaultdict(list)
    for g in range(1, base['bmax'] + 2):
        for p in pats:
            r = twin(M, w, g, p, maxs=20 * bt['steps'] + 10**6)
            pt = r['pat']
            if pt['kind'] != 'K': key = pt['kind']
            else:
                d = pt['desc']; m = re.match(r'2 5 1\^(\d+) 0\^3 9 1\^(\d+) \| a=1 r=1$', d)
                key = (f'CLEAN m={m.group(1)} n={m.group(2)}' if m else 'OTHER ' + d[:70]) + (' rem=' + pt['rem'][:20] if pt['rem'] != '-' else '')
            out[key].append(f'{p}@{g}')
    for k, v in sorted(out.items(), key=lambda x: -len(x[1])):
        print(f'  {len(v):5d}  {k}   e.g. {" ".join(v[:8])}', flush=True)
