"""Run a machine from a D-token configuration: tokens farthest-first (D(m) = (10)^m 1), head in G on the blank right of
them; stop at the next K-moment (G, reading 0, nothing to the right), a halt (undefined slot) or a step limit.
python tokrun.py MACHINE "m1 m2 ... " [maxsteps] [nK]"""
import sys
sys.path.insert(0, '../bb8_champ35_1RB0RA_1LC0RH')
from tmlit import Sim, ST

def word(toks):
    return ''.join('10' * m + '1' for m in toks)

def parse_left(s):
    """D-token parse right-to-left from the cell left of the head; returns (tokens farthest-first, clean)"""
    t = s.tape; p = s.pos - 1; lo = s.lo
    tok = []
    while p >= lo and t[p] == 1:
        m = 0; p -= 1
        while p - 1 >= lo and t[p] == 0 and t[p - 1] == 1:
            m += 1; p -= 2
        tok.append(m)
    clean = all(t[i] == 0 for i in range(lo, p + 1))
    rest = ''.join(map(str, t[lo:p + 1])).lstrip('0')
    return tok[::-1], clean, rest

def rle(v):
    out = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        out.append(str(v[i]) + ('*%d' % (j - i) if j - i > 1 else '')); i = j
    return ' '.join(out)

def start(tm, toks, state='G'):
    w = word(toks)
    return Sim.from_word(tm, '00' + w + '0', 2 + len(w), state, size=1 << 18)

def kmoment(s, gstate=6):
    if s.state != gstate or s.tape[s.pos] != 0: return False
    lo, hi = s.bounds()
    return hi <= s.pos or all(s.tape[i] == 0 for i in range(s.pos + 1, hi + 1))

def realK(s):
    tk, clean, rest = parse_left(s)
    return len(tk) >= 3 and tk[-1] == 2 and tk[-2] % 3 == 1 and tk[-3] % 3 == 1

def run_to_next(s, maxsteps=10**7, gstate=6, real=True):
    first = True
    while s.steps < maxsteps:
        if not first and kmoment(s, gstate) and (not real or realK(s)):
            return 'K'
        first = False
        if not s.step():
            return 'HALT'
    return 'TIME'

if __name__ == '__main__':
    tm = sys.argv[1]
    toks = [int(x) for x in sys.argv[2].replace(',', ' ').split()]
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 10**6
    nk = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    s = start(tm, toks)
    for i in range(nk):
        r = run_to_next(s, N)
        if r == 'K':
            tk, clean, rest = parse_left(s)
            print(r, s.steps, ('' if clean else '<' + rest[:60] + '> ') + rle(tk))
        else:
            print(r, s.steps, s.last and (ST[s.last[0]] + str(s.last[1])), s.show()[:300])
            break
