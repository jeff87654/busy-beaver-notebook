import idle
"""mk_t4.py: rows of halt_redirect/c7/mf_out.tsv whose mf35g verdict came from stage >= 2 (t reset to 0 there) and whose
undefined slot(s) survive backref_s (depth 20, 50000 nodes).  Output list_t4.txt: name machine kind nstages."""
import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_resid\tools')
import backref_s
MF = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\halt_redirect\c7\mf_out.tsv'
out = []; nrej = 0
for l in open(MF):
    p = l.rstrip('\n').split('\t')
    if len(p) < 3: continue
    m, k, ns = p[0], p[1], int(p[2])
    if k in ('LOOP', 'MAXSTAGES') or (k in ('WIDE', 'HALT') and ns >= 2):
        res = backref_s.check(m, depth=20, maxnodes=50000)
        if any('POSSIBLE' in v or 'UNDECIDED' in v for _, v in res): out.append((m, k, ns))
        else: nrej += 1
with open('list_t4.txt', 'w') as f:
    for i, (m, k, ns) in enumerate(out): f.write('t%04d %s %s %d\n' % (i, m, k, ns))
import collections
print(len(out), 'kept', nrej, 'unreachable', collections.Counter(k for _, k, _ in out))
