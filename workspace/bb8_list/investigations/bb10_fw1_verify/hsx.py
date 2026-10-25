"""exact hybrid run (Python R1/R2 with big ints, literal specials); prints specials with sizes.
   hsx.py LIST:A MAXMOVES"""
import sys
from fw import *
from hs import std_move, literal_next
from btrace import parse_list


def short(L):
    return fmt([x if x < 10 ** 6 else -1 for x in L]) if all(isinstance(x, int) for x in L) else str(L)


def big(x):
    return str(x) if x < 10 ** 12 else '~2^%d' % x.bit_length()


_ts, A = sys.argv[1].rsplit(':', 1)
L, A = parse_list(_ts), int(A)
cnt = {}
for it in range(int(float(sys.argv[2]))):
    mv = std_move(L, A)
    if mv:
        k, L, A = mv
        cnt[k] = cnt.get(k, 0) + 1
        if A > 10 ** 400:
            print('A too big', big(A), short(L)); break
        continue
    if A > 10 ** 6 or max(L) > 10 ** 6:
        print('special with big values: [%s | %s]' % (' '.join(big(x) for x in L), big(A))); break
    kind, L2, A2, st, evs = literal_next(L, A)
    print('SPECIAL %s [%s | %d] -> ' % (cnt, fmt(L), A), kind, ('[%s | %d]' % (fmt(L2), A2)) if kind == 'B' else show(L2)[:250], st, flush=True)
    cnt = {}
    if kind != 'B':
        break
    L, A = L2, A2
