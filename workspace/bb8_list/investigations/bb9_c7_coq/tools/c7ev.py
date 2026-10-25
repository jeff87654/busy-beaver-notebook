"""C7 from a Kt-type word; at each H0 event print the full tape (token view) and at the first B-at-right-end moment
after each H0 event print it too.  python c7ev.py 'frame|toks|m|r|t' maxsteps [maxev]"""
import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim, rle
from c7sim import C7, ktword, parse_toks, view
frame, toks, m, r, t = sys.argv[1].split('|')
s = Sim(C7, ktword(frame, parse_toks(toks), int(m), int(r), int(t)), state='B')
maxs = int(sys.argv[2]); maxev = int(sys.argv[3]) if len(sys.argv) > 3 else 50
nev = 0; armed = False
while s.steps < maxs and nev < maxev:
    if s.q == 'H' and s.t[s.pos] == 0:
        nev += 1; armed = True
        print('H0 #%d step=%d | %s' % (nev, s.steps, view(s)))
    if not s.step():
        print('HALT', s.steps, view(s)); break
    if armed and s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) == s.pos - 1:
        armed = False
        print('  B> step=%d | %s' % (s.steps, view(s)))
print('END', s.steps)
