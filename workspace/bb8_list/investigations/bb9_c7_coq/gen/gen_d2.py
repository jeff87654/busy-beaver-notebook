"""D2 stage: Kt (repeat 1 (5q+11) ++ [2;4;21;4]) 1 (r+5) 6 -->* Kt (repeat 1 (3q+4) ++ [3q+11; 2r+8; 2; 21; 4]) 0 4 8,
and the halt: Kt (1 :: ds) 0 4 t halts (machine level)."""
import sys, time
from common import *
from shapes import *
import mexp


def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')


START = KK(6, accr(5, 'r'), tok(1), list(Z) * 11 + [run(Z * 5, q=1)] + tok(2) + tok(4) + tok(21) + tok(4))
TARGET = KK(8, accr(4), tok(0), list(Z) * 4 + [run(Z * 3, q=1)] + tok(11, 'q', (0, 1) * 3)
            + tok(8, 'r', (0, 1, 0, 1)) + tok(2) + tok(21) + tok(4))
HSTART = ('B', [1, 0, 0, 1, run(TB, t=1), 1, 1] + accr(4) + tok(0) + list(Z) + [1, V('l')], [BLANK], '>')


def gen():
    out = []
    t0 = time.time()
    tree = mexp.explore(START, TARGET, splits=0)
    g = mexp.Gen('D2')
    rule = mexp.rule_lemma('D2STAGE', START, TARGET, tree, g, progress=True)
    out += g.lemmas + [rule]
    print('d2: %d lemmas (%.1fs)' % (len(g.lemmas), time.time() - t0), file=sys.stderr)
    tree = mexp.explore(HSTART, None, splits=0)
    assert tree.get('halt') and len(tree['items']) == 1
    _, ops, a, b = tree['items'][0]
    out.append(coqgen.stage_lemma('HALTRUN', a, ops, b))
    cn, vs = coqgen.free_vars(b)
    out.append('Lemma HALTED : forall %s, halted tm (%s).\nProof. intros. reflexivity. Qed.\n'
               % (' '.join(cn + vs), coqgen.cfg_coq(b)))
    return out


if __name__ == '__main__':
    pl.LEMMAS.clear()
    lem = gen()
    text = header('d2 test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lem)
    open(sys.argv[1], 'w', newline='\n').write(text)
