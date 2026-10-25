"""lever2.py: n1 no-far restart [1^141 | 1 | R] with (10)^j (and 1^j) right of the word at odd gaps: counter m vs 4R+3."""
import re
from rlib import twin, word
N1 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC'
for R in (19, 79, 259):
    w = word([1] * 141 + [1, R])
    b = twin(N1, w, 10**6, '-')['base']
    for j in range(1, 11):
        res = []
        for g in (1, 3, 2 * R + 3 - 2 * j):
            if g < 1: continue
            p = twin(N1, w, g, '10' * j, maxs=40 * b['steps'])['pat']
            d = p.get('desc', p.get('raw')); m = re.match(r'2 5 1\^(\d+) 0\^3 9 1\^(\d+) \| a=1 r=1$', d or '')
            res.append(f'g={g}: ' + (f'm=4R+{int(m.group(1)) - 4*R} n={m.group(2)}' if m else d[:40]) + (f' rem={p["rem"][:12]}' if p.get('rem', '-') != '-' else ''))
        print(f'R={R} (10)^{j}: ' + ' ; '.join(res), flush=True)
