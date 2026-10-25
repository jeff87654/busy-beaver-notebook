import sys, os, collections
"""stopcls.py DIR: STOP/KILLED/END rows of DIR/tree.tsv grouped by (jumps, last view prefix)."""
d = sys.argv[1]; g = collections.Counter(); ex = {}
for l in open(os.path.join(d, 'tree.tsv')):
    p = l.rstrip('\n').split('\t')
    if p[2] not in ('STOP', 'KILLED', 'END'): continue
    J = []
    with open(os.path.join(d, p[0] + '.txt'), errors='replace') as f:
        for x in f:
            if x.startswith('J'): J.append(x.split('|', 1)[1].strip()[:45] if '|' in x else '')
    key = (len(J), J[-1] if J else '')
    g[key] += 1; ex.setdefault(key, p[1])
for k, n in g.most_common(): print(n, k[0], repr(k[1]), ex[k])
