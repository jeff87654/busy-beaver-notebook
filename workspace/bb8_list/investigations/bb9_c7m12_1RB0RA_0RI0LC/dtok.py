"""Tokenise tr9 snapshots into K-grammar tokens: D(m) = (10)^m 1, runs of other cells kept raw.
  tr9 ... | python dtok.py [SUFFIX] [MAXCHARS]
Reads the RLE line, expands it, strips SUFFIX (+ head cell) from the right, then parses right-to-left:
the trailing (10)^y run is printed as b-block y, then D tokens (m values) until something else."""
import re
import sys

sys.path.insert(0, '.')
from rle import expand  # noqa: E402

suffix = sys.argv[1] if len(sys.argv) > 1 else ''
maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 300
hdr = None


def tokens(s):
    # parse left-to-right into D(m) tokens where possible; raw chars otherwise
    out = []
    i = 0
    n = len(s)
    raw = ''
    while i < n:
        j = i
        m = 0
        while j + 1 < n and s[j] == '1' and s[j + 1] == '0':
            j += 2
            m += 1
        if j < n and s[j] == '1' and (j + 1 >= n or s[j + 1] == '1' or True):
            # D(m) ends with this 1
            if raw:
                out.append('"' + raw + '"')
                raw = ''
            out.append(str(m))
            i = j + 1
        else:
            raw += s[i]
            i += 1
    if raw:
        out.append('"' + raw + '"')
    return out


for line in sys.stdin:
    if not line.startswith('  '):
        hdr = line.strip().split(':')[0]
        continue
    desc = line.strip()
    w, h, q = expand(desc)
    w = w[:h] if h is not None else w
    s = w
    if suffix and s.endswith(suffix):
        s = s[:-len(suffix)]
        m = re.search(r'(10)*$', s)
        y = len(m.group(0)) // 2
        body = s[:len(s) - 2 * y]
        tail = f' | b-run {y}'
    else:
        body, tail = s, ' | (no suffix)'
    print(hdr, ' '.join(tokens(body))[-maxc:], tail)
