"""literal next B-form for a list of configs, printed with compressed blocks.  probe.py 'LIST:A' ..."""
import sys
from fw import *
from hs import literal_next
from btrace import parse_list
from osim import comp


def show_cfg(L, A):
    out = []
    for blk, k in comp(L):
        t = ' '.join(str(x) for x in blk)
        out.append(t if k == 1 else ('%s^%d' % (t, k) if len(blk) == 1 else '(%s)^%d' % (t, k)))
    return '[%s | %d]' % (', '.join(out), A)


if __name__ == '__main__':
    for spec in sys.argv[1:]:
        ts, A = spec.rsplit(':', 1)
        L = parse_list(ts); A = int(A)
        k, L2, A2, st, evs = literal_next(L, A, 10 ** 11)
        print(show_cfg(L, A), '->', show_cfg(L2, A2) if k == 'B' else show(L2)[:250], st, 'E0=%d' % len(evs), flush=True)
