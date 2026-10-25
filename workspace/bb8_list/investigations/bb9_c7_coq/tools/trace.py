"""Literal C7 trace from a Kt word; print H0 events (and optionally B> moments) in block-RLE form with the head.
python trace.py 'frame|toks|m|r|t' maxsteps [bm]"""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
from c7sim import C7, ktword, parse_toks
from brle import brle
def show(s):
    w, l, r = s.word()
    lo = min(l, s.pos); hi = max(r, s.pos)
    return brle(w[lo:s.pos]) + ' <%s> ' % s.q + brle(w[s.pos:hi + 1])
if __name__ == '__main__':
    frame, toks, m, r, t = sys.argv[1].split('|')
    s = Sim(C7, ktword(frame, parse_toks(toks), int(m), int(r), int(t)), state='B')
    maxs = int(sys.argv[2]); bm = len(sys.argv) > 3
    while s.steps < maxs:
        if s.q == 'H' and s.t[s.pos] == 0:
            print('H0 %d | %s' % (s.steps, show(s)))
        if not s.step(): print('HALT', s.steps, show(s)); break
        if bm and s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) == s.pos - 1:
            print('B> %d | %s' % (s.steps, show(s)))
    print('END', s.steps, show(s))
