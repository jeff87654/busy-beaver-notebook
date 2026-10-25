"""Convert a D-token view (as printed by tr9 dshape/deadend: numbers m = (10)^m 1, x*k repeats, <...> raw rle)
back into a 0/1 word.   python tok2word.py "0*2 7 1*10 0 <(10)^8 0> 0*4 2 5" """
import re
import sys

sys.path.insert(0, '.')
from rle import expand  # noqa: E402


def tok2word(s):
    w = ''
    for m in re.finditer(r'<([^>]*)>|(\S+)', s):
        if m.group(1) is not None:
            w += expand(m.group(1))[0]
            continue
        t = m.group(2)
        if '*' in t:
            v, k = t.split('*')
            w += ('10' * int(v) + '1') * int(k)
        else:
            w += '10' * int(t) + '1'
    return w


if __name__ == '__main__':
    print(tok2word(sys.argv[1]))
