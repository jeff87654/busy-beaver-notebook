"""children.py BASE SLOT : list 8-state children of a 7-state BASE whose undefined SLOT (e.g. E0) is redirected to the
new state H; H's two transitions range over all (write, move, target in A..H) plus halt, at least one H slot halts
(otherwise no halt exists and the child never halts).  Prints one machine per line.  --same: also the 28 same-state
redirects (slot -> (w,d,X), X in A..G; these have no halt at all and never halt)."""
import sys
base, slot = sys.argv[1], sys.argv[2]
rows = base.split('_'); q = ord(slot[0]) - 65; c = int(slot[1])
assert rows[q][3*c:3*c+3] == '---', 'slot is not undefined'
opts = [f'{w}{d}{t}' for w in '01' for d in 'LR' for t in 'ABCDEFGH'] + ['---']
out = []
for w in '01':
    for d in 'LR':
        r = list(rows); r[q] = r[q][:3*c] + f'{w}{d}H' + r[q][3*c+3:]
        for h0 in opts:
            for h1 in opts:
                if h0 != '---' and h1 != '---': continue
                out.append('_'.join(r + [h0 + h1]))
if '--same' in sys.argv:
    for w in '01':
        for d in 'LR':
            for t in 'ABCDEFG':
                r = list(rows); r[q] = r[q][:3*c] + f'{w}{d}{t}' + r[q][3*c+3:]; out.append('_'.join(r))
print('\n'.join(out))
