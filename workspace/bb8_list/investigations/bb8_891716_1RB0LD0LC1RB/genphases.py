"""Machine-level rule lemmas by phases: explore(start_i, X_i) for each loop result X_i (engine + coqgen from bb8_list/autoproof)."""
import sys, os, time
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine, coqgen, coqgen_util

def split_phases(start, target, maxph=8):
    ph = []
    cfg = start
    tc = pl.canon(target)
    for i in range(maxph):
        ops, c2, how = engine.run_until_stuck(cfg, tc, target=target)
        if how == 'target':
            ph.append((cfg, target, False))
            return ph
        if how != 'stuck':
            raise Exception('halt?')
        lp = engine.accelerate(c2, 1)
        if lp is None:
            raise Exception('no loop at %s' % pl.show(c2))
        ph.append((cfg, lp['result'], True))
        cfg = lp['result']
    raise Exception('too many phases')

def gen_rule(name, start, target, positive=()):
    pl.set_tm(TM)
    phs = split_phases(start, target)
    texts, lemmas = [], []
    cnts, vs = coqgen.free_vars(start, target)
    args = ' '.join(cnts + vs)
    names = []
    for i, (a, b, isloop) in enumerate(phs):
        nm = '%s_ph%d' % (name, i + 1)
        tree = engine.explore(a, b, positive=frozenset(positive))
        gen = coqgen.RuleGen(nm, engine)
        txt = coqgen.rule_lemma(nm, a, b, tree, gen, progress=(i == 0), positive=positive)
        lemmas.extend(gen.lemmas)
        texts.append(txt)
        names.append(nm)
        print('  phase', i + 1, 'ok', pl.show(a), '=>', pl.show(b), file=sys.stderr)
    return lemmas + texts, names, phs

if __name__ == '__main__':
    nm = sys.argv[1]
    s, t = rules()[nm]
    lem, names, phs = gen_rule(nm, s, t)
    print('\n'.join(lem)[:3000])
