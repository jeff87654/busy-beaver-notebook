"""mpost.py TSV..: post-filter bscan output: borrow events (prefix digit x >= 10 decremented by 3 between consecutive
RSIGs, both rounds with c >= 20); prints machines with >= 1 such event and the longest consecutive chain."""
import idle  # noqa: F401  (Idle priority)

import sys, re, ast
for f in sys.argv[1:]:
    for l in open(f):
        x = l.rstrip('\n').split('\t')
        if len(x) < 6: continue
        rs = re.findall(r'(\d+):\[([^\]]*)\]:c(\d+):z(\d+)', x[5])
        cs = [int(c) for _, _, c, _ in rs]
        hist = ast.literal_eval(x[4]) if x[4] else []
        good = [h for h in hist if h[1] >= 10]
        if good and sum(1 for c in cs if c >= 20) >= 2:
            print(x[0][56:], x[1], 'nRS', x[2], 'chain', x[3], good[:6], ' '.join(f'c{c}' for c in cs[:8]))
