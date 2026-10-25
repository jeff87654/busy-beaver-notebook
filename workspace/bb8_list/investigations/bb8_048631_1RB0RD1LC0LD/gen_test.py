import sys
import planner9 as P
BL = P.BLANK
R0 = [1, 0, 0, 1, 1, BL]
start = ('E', [('run', (0,0,1), P.C(0, c=1)), ('run', (1,1,1), P.C(1, b=1)), P.V('l')], R0, '>')
tgt = ('E', [('run', (0,0,1), P.C(3, c=1)), ('run', (1,1,1), P.C(0, b=1)), P.V('l')], R0, '>')
script, end = P.drive('TL1', start, tgt, maxev=200, verbose=False)
out = open('coq_head.v.in').read()
out += '\n(** ** Crossing lemmas *)\n\n'
for nm, lm in sorted(P.LEMMAS.items()):
    out += P.crossing_lemma(nm, lm) + '\n'
out += P.lemma_text('TL1', start, tgt, script, '-->+')
open(sys.argv[1], 'w').write(out)
