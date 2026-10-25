"""Compress dtok.py output: print a line only when the token shape changes (numbers -> #, runs of equal
shapes counted). Raw strings are compressed with the rle notation."""
import re
import sys

prev = None
cnt = 0
lastline = None


def rle(s):
    out = []
    for m in re.finditer(r'(10){2,}|(01){2,}|0{3,}|1{3,}|.', s):
        g = m.group(0)
        if len(g) >= 4 and g[:2] in ('10', '01') and g == g[:2] * (len(g) // 2):
            out.append(f'({g[:2]})^{len(g) // 2}')
        elif len(g) >= 3 and len(set(g)) == 1:
            out.append(f'{g[0]}^{len(g)}')
        else:
            out.append(g)
    return ' '.join(out)


for line in sys.stdin:
    line = line.rstrip('\n')
    line = re.sub(r'"([01]+)"', lambda m: '<' + rle(m.group(1)) + '>', line)
    parts = line.split(' ', 3)
    body = parts[3] if len(parts) > 3 else line
    # collapse repeated identical tokens: x x x x -> x*4
    toks = body.split(' ')
    comp = []
    for t in toks:
        if comp and comp[-1][0] == t:
            comp[-1][1] += 1
        else:
            comp.append([t, 1])
    body2 = ' '.join(t if c == 1 else f'{t}*{c}' for t, c in comp)
    shape = re.sub(r'\d+', '#', body2)
    if shape != prev:
        if cnt:
            print(f'      ... {cnt} similar; last: {lastline}')
        print(' '.join(parts[:3]), body2)
        prev = shape
        cnt = 0
    else:
        cnt += 1
        lastline = ' '.join(parts[:3]) + ' ' + body2
if cnt:
    print(f'      ... {cnt} similar; last: {lastline}')
