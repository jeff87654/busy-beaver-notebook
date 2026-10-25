"""Write the bound file: python gen_bound.py OUT.v   (needs machine_info.pkl from gen_machine/gen_final)"""
import sys, pickle
from pathlib import Path
from common import *
from planner8 import is_run
info = pickle.load(open('machine_info.pkl', 'rb'))
end = info['end']
q, L, R, mode = end
assert q == 'I' and mode == '<' and L[0] == 0
SYM = {0: 'S0', 1: 'S1'}

def lst(toks):
    parts, cur = [], []
    for t in toks:
        if isinstance(t, int):
            cur.append(SYM[t])
        else:
            if cur:
                parts.append('[' + ';'.join(cur) + ']'); cur = []
            if t == BLANK:
                break
            if t == ('VAR', 'l'):
                parts.append('([S1;S0]^^9 ++ [S1])^^n'); break
            assert is_run(t) and len(t[2]) == 1 and t[2][0][1] == 1
            parts.append('[%s]^^%s' % (';'.join(SYM[x] for x in t[1]), t[2][0][0]))
    if cur:
        parts.append('[' + ';'.join(cur) + ']')
    return ' ++ '.join(parts) if parts else '[]'

text = Path('bound.v.in').read_text()
text = text.replace('@CHALT@', coqgen.cfg_coq(end)).replace('@LOOP@', info['loop'][0])
text = text.replace('@LLIST@', lst(L[1:])).replace('@RLIST@', lst(R))
Path(sys.argv[1]).write_text(text, newline='\n')
print('wrote', sys.argv[1])
