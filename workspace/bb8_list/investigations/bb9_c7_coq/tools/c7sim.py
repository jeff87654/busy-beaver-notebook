"""Literal C7 simulation from a word; prints the tape (RLE token view) at every H0 event (C7: H entered from E0)
and at Kt moments (head B at the blank right end) on request.
python c7sim.py WORD maxsteps [kt]   WORD: far-first spec 'f:11|t:1*11|m:1|r:20|T:0' or a literal 0/1 string ending at the head"""
import idle, sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim, rle
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
def D(d): return '10' * d + '1'
def ktword(frame, toks, m, r, t): return frame + ''.join(D(d) for d in toks) + D(m) + '10' * r + '11' + '11111100' * t + '1001'
def parse_toks(s):
    out = []
    for it in s.split(','):
        if not it: continue
        if '*' in it: a, b = it.split('*'); out += [int(a)] * int(b)
        else: out.append(int(it))
    return out
def view(s):
    w, l, r = s.word()
    lo = min(l, s.pos); hi = max(r, s.pos)
    return rle(w[lo:hi + 1], s.pos - lo, s.q)
if __name__ == '__main__':
    frame, toks, m, r, t = sys.argv[1].split('|')
    w = ktword(frame, parse_toks(toks), int(m), int(r), int(t))
    s = Sim(C7, w, state='B')
    maxs = int(sys.argv[2]); kt = len(sys.argv) > 3
    while s.steps < maxs:
        if s.q == 'H' and s.t[s.pos] == 0:
            print('H0 step=%d | %s' % (s.steps, view(s)))
        if not s.step():
            print('HALT', s.steps, view(s)); break
        if kt and s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) == s.pos - 1:
            print('KT step=%d | %s' % (s.steps, view(s)))
    print('END', s.steps, view(s))
