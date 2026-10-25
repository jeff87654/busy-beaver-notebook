"""Aggregate follower results over behaviour classes.
  python classes.py SIGS.tsv OUT_TODO_SET.tsv RESULTS... [-- SETFILES...]
Prints machine-weighted tallies per category and per tag; writes one representative per class that has no result
yet (preferring CAND rows) to OUT_TODO_SET.tsv."""
import sys, re
from collections import OrderedDict, Counter, defaultdict
args = sys.argv[1:]
sigf, todof = args[0], args[1]
rest = args[2:]
if '--' in rest:
    i = rest.index('--'); resf, setf = rest[:i], rest[i + 1:]
else:
    resf, setf = rest, ['set_r1.tsv', 'set_r2.tsv']
cls = OrderedDict()
for l in open(sigf):
    m, s = l.rstrip('\n').split('\t'); cls.setdefault(s, []).append(m)
tag = {}
for fn in setf:
    for l in open(fn):
        f = l.rstrip('\n').split('\t'); tag.setdefault(f[0], f[1] if len(f) > 1 else '')
res = {}
for fn in resf:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 3: res[f[0]] = f[2]
def cat(line):
    if line is None: return 'PENDING'
    r = re.search(r'RESULT (\S+)', line).group(1)
    fc = int(re.search(r'full_cycles=(\d+)', line).group(1)) if 'full_cycles=' in line else 0
    st = int(re.search(r'stages=(\d+)', line).group(1)) if 'stages=' in line else 0
    if r == 'HALT':
        return 'TWO-OR-MORE-REBUILDS' if fc >= 2 else 'ONE-REBUILD' if fc == 1 else ('CHAMPION-LIKE' if st == 1 else 'GROUP-1-LIKE')
    r = r.replace('UNCLEAR-', '')
    return ('UNCLEAR-' + r if fc == 0 else f'UNCLEAR-{r}-after-{fc}-full-cycle(s)')
tally, tclass, bytag = Counter(), Counter(), defaultdict(Counter)
todo = []
for s, ms in cls.items():
    rline = next((res[m] for m in ms if m in res), None)
    c = cat(rline)
    tally[c] += len(ms); tclass[c] += 1
    for m in ms: bytag[tag.get(m, '?')][c] += 1
    if rline is None:
        rep = next((m for m in ms if tag.get(m, '').startswith('CAND')), ms[0])
        todo.append((rep, f'{tag.get(rep, "")}:n{len(ms)}'))
print('machines per category (classes):')
for c, n in sorted(tally.items()): print(f'  {c:44s} {n:5d}  ({tclass[c]})')
print('by tag:')
for t, cc in sorted(bytag.items()): print(f'  {t:10s} ' + ', '.join(f'{c}={n}' for c, n in sorted(cc.items())))
with open(todof, 'w') as f:
    for m, t in todo: f.write(f'{m}\t{t}\n')
print(len(todo), 'classes without result written to', todof)
