"""Write end.v.in: the hand-written abstract part of the round-2 end (templates filled from wrappers_end.v.in)."""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
w = (HERE / 'wrappers_end.v.in').read_text()


def out_side(name):
    m = re.search(r'Lemma W_%s : .*?-->\* Bf \((.*?)\)%%sym' % name, w)
    return m.group(1)


F24OUT = out_side('F24')
G3OUT = out_side('G3')
BLK = [1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
FLAT = '[' + ';'.join(map(str, BLK * 6)) + ']'
OUT = {0: '(repeat 1 3 ++ [0] ++ repeat 1 3 ++ [4 + A; 0; 4; 2])',
       2: '(repeat 1 3 ++ [0; 7 + A; 0; 2; 0] ++ repeat 1 5 ++ [10])',
       4: '(repeat 1 3 ++ [0; 7 + A; 2] ++ repeat 1 1 ++ [0; 0; 0] ++ repeat 1 2 ++ [2] ++ repeat 1 6 ++ [0; 9; 4])'}

head = (HERE / 'end_head.v.in').read_text()
eat_t = (HERE / 'end_eat.v.in').read_text()
tail = (HERE / 'end_tail.v.in').read_text()
txt = head
for r in range(6):
    txt += eat_t.replace('@R@', str(r)).replace('@OUT@', OUT[r - r % 2])
txt += tail
PRE2 = '0 >> 0 >> 0 >> 0 >> 1 >> [0;0;0;0;0;1]^^b *> 0 >> 0 >> 1 >> 1 >> 1 >> 0 >> 1 >> 1 >> '
assert G3OUT.startswith(PRE2), G3OUT
REST2 = G3OUT[len(PRE2):]
txt = txt.replace('@REST2@', REST2).replace('@FLAT@', FLAT).replace('@F24OUT@', F24OUT).replace('@G3OUT@', G3OUT)
(HERE / 'end.v.in').write_text(txt, newline='\n')
print('wrote end.v.in', len(txt))
