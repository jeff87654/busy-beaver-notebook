"""reach.py LOG MACHINE [Rs] : rightmost head cell (relative to the word end) in each literal stage started from the
log's J configs, with r replaced by each R; also the K-moment offset (frontier advance of the stage)."""
import sys
from rlib import twin, word, rle
from logcfg import configs
log, M = sys.argv[1], sys.argv[2]
Rs = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else '19,79,139,259,2539').split(',')]
s0, s1 = (int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else '0-999').split('-'))
for s, toks, far, desc, ev in configs(log):
    if not (s0 <= s <= s1): continue
    row = []
    for R in Rs:
        t = toks[:-1] + [R]
        r = twin(M, word(t, far), 10**6, '-', maxs=3 * 10**9)
        b = r['base']
        if R == Rs[0]: row.append("K=" + str(b.get("desc", b.get("raw")))[:60])
        row.append(f"R={R}: bmax={r['bmax']} koff={b.get('off','-')} st={b.get('steps', b.get('raw'))}")
    d = desc if len(desc) < 50 else desc[:47] + '..'
    print(f"{s:3d} {'F' if far else '-'} [{d}] :: " + ' ; '.join(row), flush=True)
