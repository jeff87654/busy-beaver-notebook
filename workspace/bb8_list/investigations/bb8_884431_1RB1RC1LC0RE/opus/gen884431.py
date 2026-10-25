"""Complete busycoq proof for 1RB1RC_1LC0RE_1LF1LD_1LA1LE_1RH1RF_0LF1LG_0LD1LA_---0RA (BB(8) holdout 884431).

  python gen884431.py OUT.v

Machine-level pieces are explored and proved by bb8_list/autoproof (engine.py / coqgen.py, with nested loops: R4b, R3b
and PASSm have loops inside loop rounds); the family, the PASS iteration and the R3m/R4m chains are the template
family_full.v.in."""
import sys, time
from pathlib import Path
from pieces import *

Gp = ('A', [BLANK], [0, 1, 1, 1, 1, ('run', (1, 1), (('n', 1),)), 0, 1] + [1] * 7
      + [('run', (1, 1, 1, 1), (('b', 1),)), BLANK], '>')                      # A> 0 1^(2n+4) 0 1^(4b+8)
G3p = ('A', [BLANK], [0, 1, 1, 1, 1, 1, 1, ('run', (1, 1), (('k', 1),)), 0, 1] + mkrun(U2, {'b': 1})
       + [0, 1, 0, 1, 1, 1] + mkrun(U, {'y': 1}) + TT, '>')                    # A> 0 1^(2k+6) (01)^(2b+3) 11 (01)^y 11 t
items = [
    ('R1m', RL['R1m'][0], RL['R1m'][1], True, ()),
    ('R2m', RL['R2m'][0], RL['R2m'][1], True, ()),
    ('PASSm', PS, PT, False, ()),
    ('R4a', start4, M, True, ()),
    ('R4b', M, Gp, False, ()),
    ('R3z', engine.subst(start3, 'b', (), 0), engine.subst(G3p, 'b', (), 0), True, ()),
    ('R3a', start3, M3, True, ()),
    ('R3b', M3, G3p, False, ('b',)),
]
pl.LEMMAS.clear()
lemmas, rules = [], []
for name, s, t, prog, pos in items:
    t0 = time.time()
    tree = engine.explore(s, t, positive=frozenset(pos))
    gen = coqgen.RuleGen(name, engine)
    rules.append(coqgen.rule_lemma(name, s, t, tree, gen, progress=prog, positive=pos))
    lemmas.extend(gen.lemmas)
    print('  %s: %d lemmas (%.1fs)' % (name, len(gen.lemmas), time.time() - t0), file=sys.stderr)


def stmt(s, t):
    cnts, vs = coqgen.free_vars(s, t)
    return 'forall %s, %s -->+ %s' % (' '.join(cnts + vs), coqgen.cfg_coq(s), coqgen.cfg_coq(t))


fam = (HERE / 'family_full.v.in').read_text().replace('@R4M_STMT@', stmt(start4, tgt4)).replace('@R3M_STMT@', stmt(start3, tgt3))
text = header('BB(8) holdout 884431: ' + TM + ' never halts') \
    + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
    + '\n(** ** Stage and loop lemmas (generated) *)\n\n' + '\n'.join(lemmas) \
    + '\n(** ** Machine-level pieces (generated) *)\n\n' + '\n'.join(rules) + '\n' + fam
Path(sys.argv[1]).write_text(text, newline='\n')
print('wrote', sys.argv[1], file=sys.stderr)
