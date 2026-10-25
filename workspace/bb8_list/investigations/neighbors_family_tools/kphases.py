"""Planner phase definitions for K-family machines with transfer factor m (parent m = 4).

    python kphases.py TM m [--h H] [PHASE ...]   -> runs the planner (planner8.drive) on each phase, verbose

Phases (tape sides written left-to-right; l, rr unknown; r, m-runs symbolic):
  TR1   : l 1 0 1 B> 0^inf              -> l 0 1^m A> 0^inf
  TR2   : l 1 0 1^r A> 0^inf            -> l 0 1^(r+m) A> 0^inf
  ENTRY : l 0 0 1^r A> 0^inf            -> l 0 1^(r+m) C> 0^inf
  LOOP  : l 0 0 1^(r+3) C> 0 rr         -> l 0 1^(r+2) C> 0 1 0 rr
  FINAL : l 1 0 1^(r+3) C> 0 (10)^i 0^inf -> l 0 1^(r+3) (01)^(i+1) B> 0^inf
  END4b : 0^inf 1 1 C> 0 (10)^i 0^inf   -> (fitted per machine; see gen_kcoq.py)
All but END4b are machine-independent statements for the whole F1 family (checked by this script).
"""
import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive

ONE = (1,)
R = {'r': 1}
I = {'i': 1}
T10 = mkrun((1, 0), I)


def phases(m, h=0):
    """h >= 0 extra concrete 1s in LOOP and FINAL (h = 1: the machine's left crossing needs a run of
    at least 4; a run of exactly 3 at FINAL is its halting reset, see neighbors_final6.md)."""
    H = [1] * h
    return {
        'TR1': (('B', [1, 0, 1, V('l')], [BLANK], '>'),
                ('A', [1] * m + [0, V('l')], [BLANK], '>')),
        'TR2': (('A', mkrun(ONE, R) + [0, 1, V('l')], [BLANK], '>'),
                ('A', [1] * m + mkrun(ONE, R) + [0, V('l')], [BLANK], '>')),
        'ENTRY': (('A', mkrun(ONE, R) + [0, 0, V('l')], [BLANK], '>'),
                  ('C', [1] * m + mkrun(ONE, R) + [0, V('l')], [BLANK], '>')),
        'LOOP': (('C', [1, 1, 1] + H + mkrun(ONE, R) + [0, 0, V('l')], [0, V('rr')], '>'),
                 ('C', [1, 1] + H + mkrun(ONE, R) + [0, V('l')], [0, 1, 0, V('rr')], '>')),
        'FINAL': (('C', [1, 1, 1] + H + mkrun(ONE, R) + [0, 1, V('l')], [0] + T10 + [BLANK], '>'),
                  ('B', [1, 0] + T10 + [1, 1, 1] + H + mkrun(ONE, R) + [0, V('l')], [BLANK], '>')),
    }


# Coq statements of the same phases (m substituted)
def coq_stmt(name, m, h=0):
    ones = lambda n: ''.join('1 >> ' for _ in range(n))
    H = ones(h)
    return {
        'TR1': 'forall l, (1 >> 0 >> 1 >> l) {{B}}> const 0 -->+ (%s0 >> l) {{A}}> const 0' % ones(m),
        'TR2': 'forall r l, ([1]^^r *> 0 >> 1 >> l) {{A}}> const 0 -->+ (%s[1]^^r *> 0 >> l) {{A}}> const 0' % ones(m),
        'ENTRY': 'forall r l, ([1]^^r *> 0 >> 0 >> l) {{A}}> const 0 -->+ (%s[1]^^r *> 0 >> l) {{C}}> const 0' % ones(m),
        'LOOP': 'forall r l rr, (1 >> 1 >> 1 >> %s[1]^^r *> 0 >> 0 >> l) {{C}}> 0 >> rr -->+ '
                '(1 >> 1 >> %s[1]^^r *> 0 >> l) {{C}}> 0 >> 1 >> 0 >> rr' % (H, H),
        'FINAL': 'forall r i l, (1 >> 1 >> 1 >> %s[1]^^r *> 0 >> 1 >> l) {{C}}> 0 >> [1;0]^^i *> const 0 -->+ '
                 '(1 >> 0 >> [1;0]^^i *> 1 >> 1 >> 1 >> %s[1]^^r *> 0 >> l) {{B}}> const 0' % (H, H),
    }[name]


if __name__ == '__main__':
    tm = sys.argv[1]
    m = int(sys.argv[2])
    h = 0
    if '--h' in sys.argv:
        h = int(sys.argv[sys.argv.index('--h') + 1])
        del sys.argv[sys.argv.index('--h'):sys.argv.index('--h') + 2]
    pl.set_tm(tm)
    ph = phases(m, h)
    names = sys.argv[3:] or list(ph)
    for w in names:
        s, t = ph[w]
        try:
            drive(w, s, t, matchers=(), maxev=300, verbose=True)
        except Exception as e:
            print('  ERROR', type(e).__name__, e)
