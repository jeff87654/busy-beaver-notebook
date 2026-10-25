"""Radius-1 neighbours of 10-state machines (any state count), for the BB(10) looper search.

  python gen_nbrs10.py PARENTS.txt OUT.tsv

Writes machine, parent index, changed transition, and `root` = 1 if the change touches one of rec14's 14 fixed
root transitions (A0 A1 B0 B1 C0 C1 D0 D1 E1 F0 F1 G0 G1 H1); changes to the other (free, branched) slots give
machines the rec14 enumeration already contains when the run reaches that slot, so `root` = 1 rows are the new territory.
"""
import sys
ROOT = {'A0', 'A1', 'B0', 'B1', 'C0', 'C1', 'D0', 'D1', 'E1', 'F0', 'F1', 'G0', 'G1', 'H1'}
parents = [l.split()[0] for l in open(sys.argv[1]) if l.strip()]
rows = {}
for pi, p in enumerate(parents):
    st = p.split('_'); n = len(st); S = 'ABCDEFGHIJKLMNOP'[:n]
    vals = ['---'] + [f'{w}{d}{q}' for w in '01' for d in 'LR' for q in S]
    cells = [st[i][3 * s:3 * s + 3] for i in range(n) for s in range(2)]
    for k in range(2 * n):
        for v in vals:
            if v == cells[k]:
                continue
            c = list(cells); c[k] = v
            m = '_'.join(c[2 * i] + c[2 * i + 1] for i in range(n))
            if m in parents or m in rows:
                continue
            nm = f'{S[k // 2]}{k % 2}'
            rows[m] = (pi, nm, int(nm in ROOT))
with open(sys.argv[2], 'w') as f:
    for m, (pi, nm, r) in rows.items():
        f.write(f'{m}\t{pi}\t{nm}\t{r}\n')
print(len(rows), 'neighbours;', sum(r for _, _, r in rows.values()), 'touch the 14 root transitions')
