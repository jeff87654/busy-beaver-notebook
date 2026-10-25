import re, sys
from tm_old import Sim
M = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_0LI0LC_1RG1LD_1LC1RH_0LH0RF_---0LA'
TAIL = '10' * 4
def D(m): return '10' * m + '1'
def W(toks): return ''.join(D(t) for t in toks) + TAIL
def start(toks):
    w = W(toks); s = Sim(M, '0' * 50 + w, None, 'F'); s.pos = 50 + len(w); s._grow(); return s
def parse(s):
    """F at right end on blank, word = tokens + tail -> token list or None"""
    if s.q != 'F' or s.t[s.pos] != 0 or s.t.rfind(1) > s.pos: return None
    st, l, r = s.word()
    if s.pos != r + 2: return None
    w = st[l:s.pos]
    if not w.endswith(TAIL): return None
    m = re.fullmatch(r'((?:(?:10)*1)*)', w[:-len(TAIL)])
    if not m: return None
    return [len(t) // 2 for t in re.findall(r'((?:10)*)1', m.group(1))]
if __name__ == '__main__':
    s = Sim(M, '0', 0, 'A')
    n = 0
    while s.steps < 200000:
        t = parse(s)
        if t is not None:
            print(s.steps, t); n += 1
            if n > 12: break
        if not s.step(): print('halt', s.steps); break
