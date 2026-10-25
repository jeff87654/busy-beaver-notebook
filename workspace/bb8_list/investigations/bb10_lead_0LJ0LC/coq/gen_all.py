"""Generate the machine-level lemmas (all pieces of parts2.PARTS) into one Coq file."""
import sys, time
from common import *
import mexp
from parts2 import PARTS
ORDER = ['R1', 'R2', 'R2z', 'PRE', 'WALK', 'BOR', 'BORz', 'BORn', 'RET', 'END', 'LASTW', 'YC', 'YEND', 'HEND']
def generate():
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name in ORDER:
        s, t, pos = PARTS[name]
        t0 = time.time()
        tree = mexp.explore(s, t, positive=frozenset(pos))
        g = mexp.Gen(name)
        if t is None:
            rules.append(halt_lemma(name, s, tree, g, pos))
        else:
            rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=False, positive=pos))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), file=sys.stderr)
    return coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
def halt_lemma(name, start, tree, gen, pos):
    lines = gen.node(tree, '  ', 0, False)
    # the generated proof ends each leaf with finish_norm; for a halting leaf we need the halted witness instead
    cnts, vs = coqgen.free_vars(start, start)
    binders = ' '.join(cnts + vs + ['(Hpos_%s : 0 < %s)' % (v, v) for v in sorted(pos)])
    return 'HALTLEMMA %s | %s | %s\n%s\n' % (name, binders, coqgen.cfg_coq(start), '\n'.join(lines))
if __name__ == '__main__':
    body = generate()
    open(sys.argv[1], 'w', newline='\n').write(body)
