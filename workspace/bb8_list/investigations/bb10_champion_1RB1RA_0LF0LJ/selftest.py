"""Self-test of r10grade's abstract stage and comparison logic on synthetic R4 rules (no Turing machine involved):
the run is started at the champion's first R4, Kd [] 0 28, and continued with the given rule."""
from fractions import Fraction as F
import r10grade as G
import hlev


def c(v):
    return (F(0), F(v))


def tmpl(P, B, S, alpha=1, beta=0):
    return {'P': [c(x) for x in P], 'B': [c(x) for x in B], 'S': [c(x) for x in S], 'alpha': alpha, 'beta': beta}


def K(t, a=0, b=0):
    return {'kind': 'K', 'list': t, 'a': c(a), 'b': c(b)}


HALT = {'kind': 'HALT', 'ones': (F(4), F(4)), 'at': ('E', 0)}

CASES = {
    'champion R4': (4, {0: K(tmpl([1], [0, 0, 3], [0, 0, 2])), 1: HALT,
                        2: K(tmpl([], [3, 0, 0], [2], beta=1)), 3: HALT}, 'EQUAL'),
    'gap-3 blocks, leading 1 (R3 boundary at depth 4, b=7)': (4, {0: K(tmpl([1], [0, 0, 0, 3], [0, 0, 0, 2])), 1: HALT,
                                             2: K(tmpl([3], [0, 0, 0, 3], [0, 0, 0, 2])), 3: HALT}, 'UNRESOLVED'),
    'gap-3 blocks, leading 3 (deeper first list)': (4, {0: K(tmpl([3], [0, 0, 0, 3], [0, 0, 0, 2])), 1: HALT,
                                             2: K(tmpl([3], [0, 0, 0, 3], [0, 0, 0, 2])), 3: HALT}, 'BEATS-CHAMPION?'),
    'digit 4 blocks (parity flips: one deep clearing)': (4, {0: K(tmpl([1], [0, 0, 4], [0, 0, 2])), 1: HALT,
                                                             2: K(tmpl([3], [0, 0, 4], [0, 0, 2])), 3: HALT}, 'BELOW'),
    'odd counters rebuild too (cycle)': (4, {r: K(tmpl([1], [0, 0, 3], [0, 0, 2])) for r in range(4)},
                                         'NONHALT-PREDICTED'),
    'BB(9) champion R4 at b0=28': (2, {0: K(tmpl([], [0, 1], [0, 2]), a=1), 1: HALT}, None),
    'last digit 3 (halts after the first clearing)': (4, {0: K(tmpl([1], [0, 0, 3], [0, 0, 3])), 1: HALT,
                                                          2: K(tmpl([3], [0, 0, 3], [0, 0, 3])), 3: HALT}, 'BELOW'),
}

if __name__ == '__main__':
    S = hlev.Setup(16)
    bad = 0
    for name, (p, rules, want) in CASES.items():
        info = {'machine': name}
        r = G.finish(info, S, ((), 0, 28), [], p, rules, {}, [], say=lambda *a: None)
        ok = want is None or r['grade'] == want
        bad += not ok
        print('%-50s %-18s key=%s %s' % (name, r['grade'], G.fmt_line(r).split('	')[2], '' if ok else '  <-- expected ' + want))
        print('      ', r['note'][:150])
    print('selftest:', 'PASS' if not bad else '%d FAILURES' % bad)
