import sys, re
def parse(w):
    """parse word into tokens D(m)=(10)^m 1; return list or None"""
    i, out = 0, []
    if not w or w[0] != '1': return None
    while i < len(w):
        if w[i] != '1': return None
        m = 0
        while i + 1 < len(w) and w[i + 1] == '0':
            m += 1; i += 2
            if i >= len(w) or w[i] != '1': return None
        out.append(m); i += 1
    return out
def rle(T):
    o = []
    for x in T:
        if o and o[-1][0] == x: o[-1][1] += 1
        else: o.append([x, 1])
    return ' '.join(str(x) if c == 1 else f'{x}^{c}' for x, c in o)
if __name__ == '__main__':
    for l in sys.stdin:
        f = l.split()
        if len(f) < 3: print(l.strip()); continue
        st, w = f[1].rstrip(':'), f[2]
        T = parse(w)
        if T is None:
            # try tail forms
            print(f[0], st, 'RAW', re.sub(r'(?:10){3,}', lambda m: f'(10)^{len(m.group(0))//2} ', w)[-120:])
        else:
            print(f[0], st, rle(T))
