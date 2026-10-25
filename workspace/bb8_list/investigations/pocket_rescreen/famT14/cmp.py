"""cmp.py: read sim.exe output on stdin, print compressed lines: tape as ones-runs separated by zero-runs.
Notation: run of k ones = k ; single 0 = ',' ; 0^j (j>1) = '|j|'; repeated identical tokens 'k,' x m -> (k)^m"""
import sys, re
def toks(r):
    out = []
    for t in r.split():
        c, _, k = t.partition('^'); k = int(k) if k else 1
        out.append((c, k))
    return out
def comp(r):
    # build list of items: ones-run k followed by zero sep
    items = []
    tt = toks(r); i = 0; lead = ''
    cur = None
    for c, k in tt:
        if c == '1': cur = k
        else:
            items.append((cur if cur is not None else 0, k)); cur = None
    if cur is not None: items.append((cur, 0))
    # compress repeats
    s = []; i = 0
    while i < len(items):
        j = i
        while j < len(items) and items[j] == items[i]: j += 1
        k, z = items[i]; m = j - i
        unit = (str(k) if k else '') + (',' if z == 1 else ('|%d|' % z if z else ''))
        s.append(unit if m == 1 else '(%s)^%d' % (unit, m))
        i = j
    return ' '.join(s)
def _main():
  for line in sys.stdin:
    p = line.split(None, 2)
    if p[0] in ('E',) and len(p) > 2:
        print(p[0], p[1], comp(p[2].strip()))
    elif p[0] == 'H' and '|' in line:
        a, b = line.split('|', 1); print(a.strip(), '|', comp(b.strip()))
    else: print(line.rstrip())
if __name__ == '__main__':
    _main()
