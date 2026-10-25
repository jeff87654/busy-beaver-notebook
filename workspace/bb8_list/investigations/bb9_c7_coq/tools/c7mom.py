"""C7 from a Kt-type word: print every B-at-right-end moment (token view, far part abbreviated) in a step window,
and H0 events.  python c7mom.py 'frame|toks|m|r|t' from_step to_step"""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim, rle
from c7sim import C7, ktword, parse_toks, view
frame, toks, m, r, t = sys.argv[1].split('|')
s = Sim(C7, ktword(frame, parse_toks(toks), int(m), int(r), int(t)), state='B')
a, b = int(sys.argv[2]), int(sys.argv[3])
while s.steps < b:
    if s.q == 'H' and s.t[s.pos] == 0 and s.steps >= a:
        print('H0 step=%d | %s' % (s.steps, view(s)))
    if not s.step():
        print('HALT', s.steps, view(s)); break
    if s.steps >= a and s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) == s.pos - 1:
        print('B> step=%d | %s' % (s.steps, view(s)))
