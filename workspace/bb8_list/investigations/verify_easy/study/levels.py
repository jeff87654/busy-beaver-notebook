"""Dependency levels of the lemmas of a generated file, weighted by proof bytes.  python -I levels.py FILE.v"""
import re, sys
src = open(sys.argv[1], encoding='utf-8').read()
LEM = re.compile(r'^(Lemma|Theorem)\s+([A-Za-z0-9_\']+)', re.M)
ms = list(LEM.finditer(src)); names = [m.group(2) for m in ms]; S = set(names)
blk = {m.group(2): src[m.start():(ms[i+1].start() if i+1 < len(ms) else len(src))] for i, m in enumerate(ms)}
deps = {n: (set(re.findall(r"[A-Za-z_][A-Za-z0-9_']*", blk[n][blk[n].find('Proof.'):])) & S) - {n} for n in names}
lvl = {}
for n in names:  # file order is a topological order
    lvl[n] = 1 + max((lvl[d] for d in deps[n]), default=-1)
L = max(lvl.values())
tot = sum(len(b) for b in blk.values())
crit = {}
for n in names:
    crit[n] = len(blk[n]) + max((crit[d] for d in deps[n]), default=0)
print(sys.argv[1], 'levels', L + 1, 'total KB %.0f' % (tot / 1024), 'crit-chain KB %.0f' % (max(crit.values()) / 1024))
for k in range(L + 1):
    xs = [n for n in names if lvl[n] == k]
    print('  level %d: %4d lemmas %7.0f KB  max lemma %5.0f KB' % (k, len(xs), sum(len(blk[n]) for n in xs) / 1024, max(len(blk[n]) for n in xs) / 1024))
