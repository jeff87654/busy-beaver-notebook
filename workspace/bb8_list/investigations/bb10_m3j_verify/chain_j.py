"""Whole M3J chain from the record end [1^36 | 6B+4], with literal specials and macro clearings whose outputs are
fakes F1, F2, ... (chosen order).  Prints the structure signature (sequence of specials/jumps with token shapes) and
the halting ones.   chain_j.py B F1,F2,...   (or -grid for a fit)"""
import sys, random
import osim
from osim import flab, macro, nextfake
from fw import *
from hs import literal_next


def run_chain(B, fakes, quiet=True):
    osim.FAKES[:] = fakes
    osim.used[:] = []
    L, A = [1] * 36, 6 * B + 4
    sig = []
    while True:
        tags = []
        while True:
            mv = macro(L, A, tags)
            if mv is None:
                break
            L, A = mv
        if A == osim.PLACE:
            A = nextfake()
        if tags:
            sig.append('J[%s]' % tags[-1].split('@')[0])
            if not quiet:
                print('   jump:', ' '.join(tags[:2] + ['..'] + tags[-2:]) if len(tags) > 4 else ' '.join(tags), '->', flab(L, A)[:240])
        kind, L2, A2, st, evs = literal_next(L, A, 10 ** 12)
        if kind != 'B':
            x = L2
            if not quiet:
                print('END', kind, show(x)[:200] if isinstance(x, dict) else x)
            return sig, kind, (x.get('ones') if isinstance(x, dict) else None), (x.get('q'), x.get('c')) if isinstance(x, dict) else None
        sig.append('S(%d)' % len(evs))
        if not quiet:
            print('SPECIAL', flab(L, A)[:200], '->', flab(L2, A2)[:240])
        L, A = L2, A2


if __name__ == '__main__':
    if sys.argv[1] == '-grid':
        rng = random.Random(int(sys.argv[2]))
        rows = []
        for t in range(int(sys.argv[3])):
            B = rng.choice([1, 6, 11])
            fk = [40 + 120 * rng.randint(2, 30) for _ in range(8)]
            sig, kind, ones, hq = run_chain(B, fk)
            rows.append((B, fk[:len(osim.used)], kind, ones, hq, ' '.join(sig)))
            print(B, fk[:len(osim.used)], kind, hq, ones, ' '.join(sig), flush=True)
    else:
        B = int(sys.argv[1]); fk = [int(x) for x in sys.argv[2].split(',')]
        sig, kind, ones, hq = run_chain(B, fk, quiet=False)
        print('SIG', ' '.join(sig), kind, hq, 'ones', ones, 'fakes used', osim.used)
