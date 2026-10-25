"""Render a tape word as run-length blocks: (10)^m written m, other bits literal; mark head."""
import re, sys
def render(w, h=None):
    out = []; i = 0
    pat = re.compile(r'(?:10){3,}')
    while i < len(w):
        m = pat.match(w, i)
        if m:
            k = (m.end() - i)//2
            seg = f'(10)^{k}'
            if h is not None and i <= h < m.end(): seg = f'(10)^{(h-i)//2}<{h-i}>...(10)^rest'
            out.append(seg); i = m.end()
        else:
            c = w[i]
            out.append(('[' + c + ']') if h == i else c); i += 1
    if h is not None and h >= len(w): out.append(f' head+{h-len(w)}')
    return ' '.join(out)
if __name__ == '__main__':
    for line in sys.stdin:
        f = line.rstrip('\n').split('\t')
        if f[2] == 'H' and len(f) > 7:
            print(f[1], f[3], f[4], f[5]+f[6], '\n   ', render(f[7], int(f[8])))
        else: print(line.strip()[:200])
