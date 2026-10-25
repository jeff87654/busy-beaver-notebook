"""Event simulator with capped accumulators (discovery tool, NOT exact): standard R1/R2 in Python, every other move by
literal simulation; whenever A exceeds CAP it is replaced by FAKE[A mod 3] (keeps the mod-3 class).
   esim.py START CAP F0,F1,F2 MAXSPECIALS [MAXMOVES]"""
import sys
from fw import *
from hs import std_move, literal_next
from btrace import parse_list


def esim(L, A, cap, fake, maxspec, maxmoves=10 ** 8, log=print):
    nspec = 0
    cnt = {'R1': 0, 'R2': 0, 'cap': 0}
    for mv_i in range(maxmoves):
        mv = std_move(L, A)
        if mv:
            k, L, A = mv
            cnt[k] += 1
            if A > cap:
                A = fake[A % 3]
                cnt['cap'] += 1
            continue
        kind, L2, A2, st, evs = literal_next(L, A)
        if kind != 'B':
            log('END %s (%s) from [%s | %d]: %s' % (kind, cnt, fmt(L), A, show(L2) if isinstance(L2, dict) else L2))
            return kind
        log('SPECIAL (%s) [%s | %d] -> [%s | %d]  %d st, %d E0' % (cnt, fmt(L), A, fmt(L2), A2, st, len(evs)))
        cnt = {'R1': 0, 'R2': 0, 'cap': 0}
        L, A = L2, A2
        nspec += 1
        if nspec >= maxspec:
            return 'MAXSPEC'
    return 'MAXMOVES'


if __name__ == '__main__':
    _, ts, A = sys.argv[1].split(':')
    cap = int(sys.argv[2]); fake = [int(x) for x in sys.argv[3].split(',')]
    esim(parse_list(ts), int(A), cap, fake, int(sys.argv[4]), int(float(sys.argv[5])) if len(sys.argv) > 5 else 10 ** 8,
         log=lambda s: print(s, flush=True))
