"""mkstarts.py LABEL [MODE] -> runs/st_LABEL.txt (renum start lines 'b<b> WORD HEAD STATE') and runs/base_LABEL.txt
MODE = halt (default): the base's first undefined read after K(0^n;0;b);  inline:SLOT : the first read of SLOT after
K(0^n;0;b), with SLOT made undefined in the written base."""
import sys
import fam
from eng import Fail
BASES = {l.split()[0]: l.split()[1:] for l in open('bases.txt') if l.strip() and not l.startswith('#')}
lbl = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else 'halt'
bs = [1, 3, 6]
base, t, n = BASES[lbl][0], BASES[lbl][1], int(BASES[lbl][2])
fam.register(lbl, base, t, n)
outl = []
rb = base
if mode.startswith('inline:'):
    slot = mode.split(':')[1]
    q, c = 'ABCDEFGHIJ'.index(slot[0]), int(slot[1])
    rows = base.split('_'); rows[q] = rows[q][:3 * c] + '---' + rows[q][3 * c + 3:]; rb = '_'.join(rows)
    for b in bs:
        w, h, st, steps = fam.inline_start(lbl, b, slot)
        outl.append(f'b{b} {w} {h} {st}'); print(f'# b={b} {slot} read at step {steps} len={len(w)}', file=sys.stderr)
else:
    for b in bs:
        w, h, st, sl = fam.start(lbl, b)
        outl.append(f'b{b} {w} {h} {st}'); print(f'# b={b} halts at {sl} len={len(w)}', file=sys.stderr)
tag = lbl + ('' if mode == 'halt' else '_' + mode.replace(':', ''))
open(f'runs/st_{tag}.txt', 'w').write('\n'.join(outl) + '\n')
open(f'runs/base_{tag}.txt', 'w').write(rb + '\n')
print(tag, rb)
