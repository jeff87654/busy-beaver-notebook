"""python gen_bound_fh.py OUT.v  (needs cfgs_fh.pkl)"""
import sys, pickle
from pathlib import Path
from common import *
from planner8 import is_run
cfg = pickle.load(open('cfgs_fh.pkl', 'rb'))
end = cfg['END']
q, L, R, mode = end
assert q == 'I' and mode == '<' and L[0] == 0
SYM = {0: 'S0', 1: 'S1'}
def lst(toks):
    parts, cur = [], []
    for t in toks:
        if isinstance(t, int):
            cur.append(SYM[t]); continue
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
text = Path('bound_fh.v.in').read_text()
text = text.replace('@CHALT@', coqgen.cfg_coq(end)).replace('@LLIST@', lst(L[1:])).replace('@RLIST@', lst(R))
Path(sys.argv[1]).write_text(text, newline='\n')
print('wrote', sys.argv[1])
