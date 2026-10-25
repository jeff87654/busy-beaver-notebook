import idle
"""Print the DEPS heredoc for verify_f3/compile_clean.sh: 'file deps...' longest first; check closure from f3/probe."""
import re, sys
from pathlib import Path
D = Path(sys.argv[1])
LOGI = {'XL': 'lib', 'XDev': 'dev', 'XK31': 'k31', 'XScore': 'score', 'F3': 'f3', 'BB8': 'lib9'}
EST = {'K_e1': 7100, 'G_sub2': 3600, 'K_e2': 2200, 'G_entry': 2000, 'G_sub4': 1900, 'G_sub5': 1700, 'G_sub3': 1600,
       'G_stop': 760, 'G_xtop': 700, 'G_p20_5': 700, 'G_p20_4': 700, 'G_p20_3': 600, 'G_p20_2': 550, 'G_p20_1': 500,
       'G_p20_0': 480, 'G_xreb1': 450, 'G_xreb2': 400, 'G_p14_5': 400, 'G_p14_4': 380, 'G_p14_3': 360, 'G_p14_2': 355, 'G_p14_1': 335, 'G_p14_0': 320,
       'K_x': 300, 'G_rules': 150, 'G_end': 100, 'K_rf': 90, 'Abs': 110}
def deps(rel):
    s = (D / (rel + '.v')).read_text(encoding='utf-8')
    s = re.sub(r'\(\*.*?\*\)', '', s, flags=re.S)
    out = []
    for m in re.finditer(r'From\s+(\w+)\s+Require\s+(?:Import\s+|Export\s+)?([^.]*)\.', s):
        d = LOGI.get(m.group(1))
        if d is None: continue
        for name in m.group(2).split():
            if (D / d / (name + '.v')).exists(): out.append(d + '/' + name)
            else: sys.exit('missing %s/%s from %s' % (d, name, rel))
    return out
allf = sorted(p.relative_to(D).with_suffix('').as_posix() for p in D.glob('*/*.v'))
DP = {f: deps(f) for f in allf}
# closure
need = set(); todo = ['f3/probe']
while todo:
    f = todo.pop()
    if f in need: continue
    need.add(f); todo += DP[f]
print('# not in probe closure:', sorted(set(allf) - need), file=sys.stderr)
# transitive deps for ordering
memo = {}
def tdeps(f):
    if f not in memo:
        s = set(DP[f])
        for d in DP[f]: s |= tdeps(d)
        memo[f] = s
    return memo[f]
# critical path length estimate for ordering (longest first)
cp = {}
def crit(f):
    if f not in cp:
        users = [g for g in allf if f in DP[g]]
        cp[f] = EST.get(f.split('/')[1], 20) + max([crit(u) for u in users], default=0)
    return cp[f]
order = sorted(allf, key=lambda f: (len(tdeps(f)) > 0 and 0, -crit(f)))
# topological stable sort by crit
done = []; rest = sorted(allf, key=lambda f: -crit(f))
while rest:
    for f in rest:
        if all(d in done for d in DP[f]):
            done.append(f); rest.remove(f); break
for f in done: print(f, ' '.join(DP[f]))
