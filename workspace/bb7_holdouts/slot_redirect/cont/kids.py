"""kids.py: reachers (HALT rows of outA/outB) -> 28 children each (first-reached slot X := w d S, S in A..G; the other
undefined slots stay) -> kids.tsv (child, base, X, base_steps, base_ones) and kin/s000 (+ controls champ_231, old champion)."""
import glob, os
H = os.path.dirname(os.path.abspath(__file__))
reach = {}
for l in open(os.path.join(H, 'reachers.tsv')):
    p = l.rstrip().split(chr(9)); reach[p[0]] = (p[1], p[2], p[3])
rows = []; kids = []
for m, (x, st, on) in sorted(reach.items()):
    q, c = ord(x[0]) - 65, int(x[1]); pos = 7 * q + 3 * c
    assert m[pos:pos + 3] == '---', (m, x)
    for w in '01':
        for d in 'LR':
            for s in 'ABCDEFG':
                k = m[:pos] + w + d + s + m[pos + 3:]
                kids.append(k); rows.append(f'{k}\t{m}\t{x}\t{st}\t{on}')
ctl = ['1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_---0LC_1RG1LD_0RG0RF']
os.makedirs(os.path.join(H, 'kin'), exist_ok=True)
open(os.path.join(H, 'kin', 's000'), 'w').write('\n'.join(kids + ctl) + '\n')
open(os.path.join(H, 'kids.tsv'), 'w').write('child\tbase\tslot\tbase_steps\tbase_ones\n' + '\n'.join(rows) + '\n')
print(len(reach), 'reachers', len(kids), 'children')
