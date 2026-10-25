import sys
sys.path.insert(0, r'../../bb10_n1_coq')
import lit
from lit import Tape, is_bform, tokens, fmt
def D(m): return '10'*m+'1'
for r in (7, 10, 13, 19, 22):
    w = D(4)+D(1)*3 + D(1) + D(r) + '1010'
    tp = Tape(w, len(w), 'G')
    seen = 0
    while tp.steps < 200000 and seen < 3:
        if not tp.step(): print('halt'); break
        b = is_bform(tp)
        if b: print('r', r, 'steps', tp.steps, 'B-form', fmt(b[0]), '| A =', b[1]); seen += 1
