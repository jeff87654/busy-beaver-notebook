import sys, re
from tokparse import parse, rle
def parseB(w):
    if not w.endswith('01'): return None
    x = w[:-2]; r = 0
    while x.endswith('10'): x = x[:-2]; r += 1
    T = parse(x)
    return None if T is None else T + [r]
def parseG(w):
    if not w.endswith('10101010'): return None
    return parse(w[:-8])
for l in sys.stdin:
    f = l.split()
    if len(f) < 3: print(l.strip()); continue
    st, w = f[1].rstrip(':'), f[2]
    for name, fn in (('G', parseG), ('B', parseB), ('T', parse)):
        T = fn(w)
        if T is not None: print(f[0], st, name, rle(T)); break
    else:
        print(f[0], st, 'RAW', re.sub(r'(?:10){3,}', lambda m: f'(10)^{len(m.group(0))//2} ', w)[-150:])
