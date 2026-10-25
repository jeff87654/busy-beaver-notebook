"""Machine-level lemmas for the champion rules of n1 (GH base): PASS, PRO (R1 prologue), R2."""
import sys, time
from pathlib import Path
from common import *
import mexp
def H(left): return ('H', list(left), [BLANK], '>')
def W(*toks, far=None):
    left = []
    for t in reversed(toks): left += t
    return H(left + (far if far is not None else [V('l')]))
ONES = lambda **v: [run((1,0,1), **v)]
RULES = [
  ('PASS', W(tok(1, c=1), tok(0, j=1)), W(tok(0, c=1), tok(2, j=1))),
  ('PRO', W(tok(3, t=1), tok(0), tok(0, a=1)), W(tok(0, t=1), tok(3, a=1), tok(2))),
  ('R2M', W(tok(3, t=1), ONES(k=1), tok(1), tok(0), tok(0, a=1)), W(tok(0, t=1), tok(3, a=1), ONES(k=1), tok(0), tok(4))),
]
def gen(rules):
    out = []
    for name, S, T in rules:
        tree = mexp.explore(S, T, splits=3)
        g = mexp.Gen(name)
        r = mexp.rule_lemma(name, S, T, tree, g, progress=True)
        out += g.lemmas + [r]
    return out
if __name__ == '__main__':
    pl.LEMMAS.clear()
    lem = gen(RULES)
    text = header('n1 base rules (test)') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lem)
    Path(sys.argv[1]).write_text(text, newline='\n')
    print('wrote', len(text))
