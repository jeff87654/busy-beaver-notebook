"""Build a configuration word from a token description, head on the blank right of it (state B).
  python dconf.py "RAW:111 (01)^7 00" "D:2,5,4,4,1" "D:40" "R:8" "RAW:1^8 00 1 00 1"
D:m1,m2,.. appends (10)^m 1 for each m; R:y appends (10)^y; RAW: appends an rle description."""
import sys

sys.path.insert(0, '.')
from rle import expand  # noqa: E402

LOUT = '111 (01)^7 1 0 11 0 11 0 11 0 11 0 11 0 11 0 11 0 11 0 11 0 111 (01)^7 00'


def build(args):
    w = ''
    for a in args:
        kind, val = a.split(':', 1)
        if kind == 'RAW':
            w += expand(val)[0]
        elif kind == 'LOUT':
            w += expand(LOUT)[0]
        elif kind == 'D':
            for m in val.split(','):
                w += '10' * int(m) + '1'
        elif kind == 'R':
            w += '10' * int(val)
        else:
            raise SystemExit('bad token ' + a)
    return w


if __name__ == '__main__':
    w = build(sys.argv[1:])
    print(w, len(w), 'B')
