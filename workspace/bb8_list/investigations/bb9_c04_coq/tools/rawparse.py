"""rawparse.py: expand a c04raw RLE line into the cell word and print it as Kt: far raw prefix, tokens far->near, m, r, t."""
import re, sys
from ktparse import parse
def expand(s):
    out = []
    for m in re.finditer(r'\(([01]+)\)\^(\d+)|([01]+)', s):
        if m.group(1): out.append(m.group(1) * int(m.group(2)))
        else: out.append(m.group(3))
    return ''.join(out)
def kt_of_line(line):
    body = line.split(' ', 2)[2].split(' [')[0]
    w = expand(body).lstrip('0')
    return parse(w)
if __name__ == '__main__':
    for line in sys.stdin:
        if line.startswith('K '):
            r = kt_of_line(line)
            if r:
                far, toks, m, rr, t = r
                # RLE the token list
                o = []; i = 0
                while i < len(toks):
                    j = i
                    while j < len(toks) and toks[j] == toks[i]: j += 1
                    o.append('%d*%d' % (toks[i], j - i) if j - i > 1 else str(toks[i])); i = j
                print(line.split()[1], 'far=%r' % far[-30:], 'toks=', ' '.join(o), 'm=%d r=%d t=%d' % (m, rr, t))
