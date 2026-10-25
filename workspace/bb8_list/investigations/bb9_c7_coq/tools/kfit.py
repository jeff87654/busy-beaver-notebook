"""Find the first B> moment whose block-RLE matches a regex, for Kt-start words; print it for several params.
python kfit.py 'REGEX' 'frame|toks|m|r|t' ...   (each spec one run)"""
import idle, sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim
from c7sim import C7, ktword, parse_toks
from brle import brle
rx = re.compile(sys.argv[1])
for spec in sys.argv[2:]:
    frame, toks, m, r, t = spec.split('|')
    sm = Sim(C7, ktword(frame, parse_toks(toks), int(m), int(r), int(t)), state='B')
    found = None
    while sm.steps < 5 * 10**7:
        if not sm.step(): found = 'HALT'; break
        if sm.q == 'B' and sm.t[sm.pos] == 0 and sm.t.rfind(1) == sm.pos - 1:
            w, lo, rr = sm.word(); b = brle(w[lo:rr + 1])
            if rx.search(b): found = '%d | %s' % (sm.steps, b); break
    print(spec, '->', found)
