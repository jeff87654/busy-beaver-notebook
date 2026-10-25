import idle
"""ttparse.py: parse runs/tt/tt_K_t.txt -> next top or exit, vs h003 rule; plus the final outcome."""
import glob, re, os
RULE = {1: (9, 36), 4: (3, -2), 3: (3, 16)}
rows = []
for f in glob.glob('runs/tt/*.txt'):
    K, t = map(int, os.path.basename(f)[3:-4].split('_'))
    J = []; end = 'RUNNING/KILLED'
    for l in open(f, errors='replace'):
        if l.startswith('J'): J.append(l)
        elif l.startswith(('HALT', 'STOP', 'END')): end = ' '.join(l.split()[:2]) + ((' ones ' + l.split('ones ')[1].split()[0]) if 'ones' in l else '')
    nxt = 'none'
    for l in J[1:]:
        v = l.split('|', 1)[1].strip()
        mm = re.fullmatch(r'0\*2 7 1\*(\d+)', v)
        if mm: nxt = int(mm.group(1)); break
        if not v.startswith('0 1 '): nxt = 'exit'; break
    r = K % 5
    pred = (RULE[r][0] * K + 60 * 366 + RULE[r][1]) // 5 if r in RULE else 'exit'
    rows.append((K, t, K % 25, nxt, pred, 'OK' if nxt == pred else 'MISMATCH', end, len(J)))
for r in sorted(rows, key=lambda x: (x[1], x[0])): print(*r)
