"""Run mexp.py symbolic proof generator on n1_GH_---0LJ_0LE0LJ and any other gadget variants!"""
import sys, time
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb10_n1_coq')
import planner8 as pl
import engine, coqgen, mexp
from evs import EV
from gen_base import RULES as BASE

ORDER = ['H', 'S0', 'P1', 'P2', 'P3', 'P4', 'E']

def test_symbolic(name, tm):
    print(f"=== Symbolic mexp test for {name}: {tm} ===", flush=True)
    t0 = time.time()
    pl.set_tm(tm)
    pl.LEMMAS.clear()
    mexp.FRESH = mexp.itertools.count()
    out = []
    for rname, S, T in BASE:
        tree = mexp.explore(S, T, splits=3)
        g = mexp.Gen(rname)
        r = mexp.rule_lemma(rname, S, T, tree, g, progress=True)
        out += g.lemmas + [r]
    for rname in ORDER:
        S, T = EV[rname][:2]
        pos = frozenset(EV[rname][2]) if len(EV[rname]) > 2 else frozenset()
        tree = mexp.explore(S, T, splits=4, positive=pos)
        g = mexp.Gen('X' + rname)
        r = mexp.rule_lemma('EV_' + rname, S, T, tree, g, progress=False, positive=sorted(pos))
        out += g.lemmas + [r]
    S = EV['HALT'][0]
    tree = mexp.explore(S, None, splits=0)
    assert tree.get('halt') and all(it[0] != 'split' for it in tree['items'])
    end = tree['end']
    print(f"  ALL SYMBOLIC RULES PROVED in {time.time() - t0:.2f}s! ({len(out)} lemmas)", flush=True)
    print(f"  HALT end configuration: {mexp.show(end)}", flush=True)
    print(f"  Coq HALT end: {coqgen.cfg_coq(end)}", flush=True)

if __name__ == '__main__':
    test_symbolic('n1 (0LJ0LI_---0LC)', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_0LJ0LI_---0LC')
    test_symbolic('n1_plus1 (---0LJ_0LE0LJ)', '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LI0LC_0RG1LD_1RH1LG_1LC0RG_---0LJ_0LE0LJ')
