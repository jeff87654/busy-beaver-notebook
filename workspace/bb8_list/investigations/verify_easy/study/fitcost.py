"""Per-lemma compile time (from coqc -time) vs. simple cost proxies.  python -I fitcost.py FILE.v FILE.time.txt"""
import re, sys
src = open(sys.argv[1], encoding='utf-8').read()
b = src.encode('utf-8')
LEM = re.compile(r'^(Lemma|Theorem)\s+([A-Za-z0-9_\']+)', re.M)
ms = list(LEM.finditer(src))
# char offsets in -time are byte offsets
starts = [len(src[:m.start()].encode('utf-8')) for m in ms]
names = [m.group(2) for m in ms]
t = [0.0] * len(ms)
for line in open(sys.argv[2], encoding='utf-8', errors='replace'):
    m = re.match(r'Chars (\d+) - \d+ \[.*\] ([\d.]+) secs', line)
    if not m: continue
    off = int(m.group(1)); 
    import bisect
    i = bisect.bisect_right(starts, off) - 1
    if i >= 0: t[i] += float(m.group(2))
rows = []
for i, m in enumerate(ms):
    blk = src[m.start():(ms[i+1].start() if i + 1 < len(ms) else len(src))]
    stmt = blk[:blk.find('Proof.')]
    steps = sum(int(x) for x in re.findall(r'do (\d+) step', blk)) + 1
    rows.append((names[i], t[i], len(blk), len(stmt), steps))
import math
for name, f in [('bytes', lambda r: r[2]), ('steps', lambda r: r[4]), ('steps*stmt', lambda r: r[4] * r[3])]:
    xs = [f(r) for r in rows]; ys = [r[1] for r in rows]
    k = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
    err = sum((y - k * x) ** 2 for x, y in zip(xs, ys)); var = sum((y - sum(ys) / len(ys)) ** 2 for y in ys)
    print('%-11s R2 %.3f   k=%.3g s/unit' % (name, 1 - err / var, k))
print('total %.1f s over %d lemmas' % (sum(t), len(rows)))
