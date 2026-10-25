"""shapes.py: read rounds output on stdin, compress each 'before => after' pair into a shape and count"""
import sys, re, collections
def comp(s):
    toks = s.split()
    out = []
    i = 0
    while i < len(toks):
        j = i
        while j < len(toks) and toks[j] == toks[i]: j += 1
        t = toks[i]
        m = re.match(r'^(\d+)(.*)$', t)
        n = int(m.group(1)); n = str(n) if n <= 9 else 'X'
        t = n + m.group(2)
        cnt = j - i
        out.append(t if cnt == 1 else (t + '^' + ('k' if cnt > 3 else str(cnt))))
        i = j
    return ' '.join(out)
cnt = collections.Counter(); ex = {}
for line in sys.stdin:
    if '|' not in line or '=>' not in line: continue
    body = line.split(' | ', 1)[1]
    a, b = body.split('=>')
    key = comp(a) + '  =>  ' + comp(b)
    cnt[key] += 1
    ex.setdefault(key, line.strip()[:200])
for k, v in cnt.most_common():
    print(f'{v:7d}  {k}')
