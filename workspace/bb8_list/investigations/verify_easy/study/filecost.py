"""Cost proxy (sum over lemmas of steps x statement length) per generated file vs measured times.
   python -I filecost.py PKGDIR compile_clean.log"""
import re, sys, os
root, logf = sys.argv[1], sys.argv[2]
meas = {m.group(1): int(m.group(2)) for m in re.finditer(r'(\S+)\.v ok, (\d+) s', open(logf).read())}
LEM = re.compile(r'^(Lemma|Theorem)\s+([A-Za-z0-9_\']+)', re.M)
rows = []
for f in sorted(meas):
    p = os.path.join(root, f + '.v')
    if not os.path.exists(p): continue
    src = open(p, encoding='utf-8').read(); ms = list(LEM.finditer(src)); c = 0
    for i, m in enumerate(ms):
        blk = src[m.start():(ms[i+1].start() if i + 1 < len(ms) else len(src))]
        stmt = blk[:blk.find('Proof.')] if 'Proof.' in blk else blk
        c += (sum(int(x) for x in re.findall(r'do (\d+) step', blk)) + 3 * len(re.findall(r'execute', blk)) + 1) * len(stmt)
    rows.append((f, meas[f], c))
rows.sort(key=lambda r: -r[1])
for f, t, c in rows[:30]:
    print('%-18s %6d s  cost %10.3g  s/Gunit %.1f' % (f, t, c, t / (c / 1e9) if c else 0))
