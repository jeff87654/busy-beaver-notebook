"""gen_all.py OUT.v : assemble ALL C04 machine lemmas in ONE process (dedup crossings + rot_*), then the R0 abstract
   layer, into a single file.  Rebuild (REBUILD1), rules (R1/R2/R3), 24 sub-steps, 6 stop, 6 entry.
   The cascade / endgame / score abstract parts are appended later (separate templates)."""
import sys, time, pickle
from common import *
from shapes import *
import mexp
import gen_rules, gen_reb1, gen_rules_z

def main(out):
    pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
    lemmas = []
    t0 = time.time()
    # R1/R2/R3
    for name, s, t, pos in gen_rules.ITEMS:
        tree = mexp.explore(s, t, positive=frozenset(pos))
        g = mexp.Gen(name); lemmas += g.lemmas + [mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos)]
    # R2z/R3z
    for name, s, t, pos in gen_rules_z.ITEMS:
        tree = mexp.explore(s, t, positive=frozenset(pos))
        g = mexp.Gen(name); lemmas += g.lemmas + [mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos)]
    # REBUILD1
    lem, rule = gen_reb1.gen(); lemmas += lem + [rule]
    print('after rebuild %.0fs' % (time.time() - t0), file=sys.stderr)
    # 24 sub-steps
    import d0spec
    for C in (2, 3, 4, 5):
        for E in range(6):
            S, Tg, _ = pickle.load(open('tree_sub_%d_%d.pkl' % (C, E), 'rb'))
            tree = mexp.explore(S, Tg, splits=0)
            g = mexp.Gen('S%d_%d' % (C, E)); lemmas += g.lemmas + [mexp.rule_lemma('SUB%d_%d' % (C, E), S, Tg, tree, g, progress=True)]
    # 6 stop, 6 entry
    for e in range(6):
        S, Tg, _ = pickle.load(open('tree_stop_%d.pkl' % e, 'rb')); tree = mexp.explore(S, Tg, splits=0)
        g = mexp.Gen('STOP%d' % e); lemmas += g.lemmas + [mexp.rule_lemma('STOP_%d' % e, S, Tg, tree, g, progress=True)]
    for e in range(6):
        S, Tg, _ = pickle.load(open('tree_entry_%d.pkl' % e, 'rb')); tree = mexp.explore(S, Tg, splits=0)
        g = mexp.Gen('ENTRY%d' % e); lemmas += g.lemmas + [mexp.rule_lemma('ENTRY_%d' % e, S, Tg, tree, g, progress=True)]
    print('generated %.0fs, %d lemma blocks' % (time.time() - t0, len(lemmas)), file=sys.stderr)
    text = header('C04 all machine lemmas') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas)
    open(out, 'w', newline='\n').write(text)
    print('wrote', out, len(text), file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv[1])
