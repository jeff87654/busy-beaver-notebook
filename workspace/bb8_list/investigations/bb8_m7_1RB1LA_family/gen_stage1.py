"""Stage 1: machine-level lemmas (engine-generated) for the 1RB1LA family; prints lemma statements."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
from segs import *
import coqgen, coqgen_util
import passcfg
pl.LEMMAS.clear()
texts = []

def gen(name, s, t, progress, pos=()):
    t0 = time.time()
    tree = engine.explore(s, t, positive=frozenset(pos))
    g = coqgen.RuleGen(name, engine)
    txt = coqgen.rule_lemma(name, s, t, tree, g, progress=progress, positive=pos)
    texts.extend(g.lemmas + [txt])
    print('  %s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), file=sys.stderr)

def stmt(s, t, arrow='-->+'):
    cnts, vs = coqgen.free_vars(s, t)
    return 'forall %s, %s %s %s' % (' '.join(cnts + vs), coqgen.cfg_coq(s), arrow, coqgen.cfg_coq(t))

def build():
    S = segs()
    gen('R1m', *R['R1m'], True)
    gen('Pass', *passcfg.pass_rule(), True)
    gen('PassB', *passcfg.passb_rule(), True)
    for nm in ('R3A0', 'R3A1', 'R3B0', 'R3B1', 'R3C0', 'R3C1', 'R4_0', 'R4_1'):
        s, t, prog = S[nm]
        gen(nm, s, t, prog)
    return texts

if __name__ == '__main__':
    build()
    for t in texts:
        for line in t.split('\n'):
            if line.startswith('Lemma') or line.startswith('Theorem'):
                print(line[:1200])
