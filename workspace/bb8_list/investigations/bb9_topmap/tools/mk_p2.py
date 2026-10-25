import sys, os, re, glob
"""mk_p2.py OUT: pass-2 list from runs/A_*/tree.tsv: STOP/KILLED/END rows minus (a) runs stuck after J1 (<= 1 jump) and
(b) runs whose top K list (any '... 1*K' view, K >= 1000, same prefix shape) has periodic differences (period <= 4, +-20)
covering ALL their late jumps (exact rebuild loops).  Lines 'name machine'."""
TOP = re.compile(r'^((?:\S+ )*?)1\*(\d+)$')
out = open(sys.argv[1], 'w'); n = 0
for tsv in sorted(glob.glob('runs/A_*/tree.tsv')):
    d = os.path.dirname(tsv); var = os.path.basename(d)[2:]
    for l in open(tsv):
        p = l.rstrip('\n').split('\t')
        if p[2] not in ('STOP', 'KILLED', 'END'): continue
        J = []
        for x in open(os.path.join(d, p[0] + '.txt'), errors='replace'):
            if x.startswith('J') and '|' in x: J.append(x.split('|', 1)[1].strip())
        if len(J) <= 1: continue
        tops = {}
        for v in J:
            mm = TOP.match(v)
            if mm and int(mm.group(2)) >= 1000 and len(mm.group(1).split()) <= 5:
                tops.setdefault(re.sub(r'\d{3,}', 'X', mm.group(1)), []).append(int(mm.group(2)))
        arith = False
        for ks in tops.values():
            dif = [b - a for a, b in zip(ks, ks[1:])]
            if any(len(dif) >= q + 1 and all(abs(dif[i] - dif[i - q]) <= 20 for i in range(q, len(dif))) for q in (1, 2, 3, 4)): arith = True
        if arith: continue
        out.write('%s_%s %s\n' % (var, p[0], p[1])); n += 1
print(n)
