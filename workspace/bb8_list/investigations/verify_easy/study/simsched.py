"""Simulate the build schedule (list scheduling, largest/most-critical first) for J = 1, 2, 4, 8, 16, 32 coqc.

    python -I simsched.py DEPS.txt TIMES [TIMES...] [--proxy TREE] [--slow X]

DEPS.txt: coqdep output for the tree (verify.sh writes it to _verify/deps.txt).
TIMES: files with lines "<path>.v ok, <n> s" (compile_clean.sh logs) or "<path>.vo (real: <n> s)" (verify.sh logs);
later files override earlier ones.  --proxy TREE: files without a measured time get 5.5e-5 s per cost unit
(split_generated.cost) + 8 s, from the sources in TREE.  --slow X divides all times by X (e.g. 2.5 for a
dedicated core instead of our shared machine at Idle priority).
Prints, per J, the simulated wall time and the critical path (longest dependency chain)."""
import re, sys, os, heapq
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pkg', 'tools'))
args = sys.argv[1:]
proxy = None; slow = 1.0
if '--proxy' in args:
    i = args.index('--proxy'); proxy = args[i + 1]; del args[i:i + 2]
if '--slow' in args:
    i = args.index('--slow'); slow = float(args[i + 1]); del args[i:i + 2]
deps = {}
for line in open(args[0], encoding='utf-8', errors='replace'):
    line = line.rstrip('\r\n')
    if ': ' not in line: continue
    tgt, rest = line.split(': ', 1)
    tgt = tgt.split()[0]
    if not tgt.endswith('.vo'): continue
    deps[tgt[:-3]] = [w[:-3] for w in rest.split() if w.endswith('.vo')]
files = set(deps)
for f in files:
    deps[f] = [d for d in deps[f] if d in files and d != f]
T = {}
for tf in args[1:]:
    for line in open(tf, encoding='utf-8', errors='replace'):
        m = re.search(r'(\S+)\.v ok, (\d+) s', line) or re.search(r'(\S+)\.vo \(real: ([\d.]+)', line)
        if m: T[m.group(1)] = float(m.group(2))
missing = [f for f in files if f not in T]
if proxy:
    import split_generated as sg
    for f in files:
        src = open(os.path.join(proxy, f + '.v'), encoding='utf-8').read()
        if f in T and 'split by tools/split_generated.py' not in src: continue
        r = sg.parse(src)
        T[f] = 8 + (5.5e-5 * sum(sg.cost(b) for _, b in r[1]) if r else 0)
    missing = []
for f in missing:
    T[f] = 10.0
T = {f: t / slow for f, t in T.items()}
# critical path / bottom level
bl = {}
def bottom(f):
    if f in bl: return bl[f]
    users = [g for g in files if f in deps[g]]
    bl[f] = T[f] + max((bottom(g) for g in users), default=0)
    return bl[f]
sys.setrecursionlimit(10000)
users = {f: [] for f in files}
for g in files:
    for d in deps[g]: users[d].append(g)
order = []
seen = set()
def topo(f):
    if f in seen: return
    seen.add(f)
    for d in deps[f]: topo(d)
    order.append(f)
for f in sorted(files): topo(f)
for f in reversed(order):
    bl[f] = T[f] + max((bl[g] for g in users[f]), default=0)
crit = max(bl.values())
print('files %d, total %.0f s, critical path %.0f s%s' % (len(files), sum(T.values()), crit,
      ' (missing times: %d)' % len(missing) if missing else ''))
for J in (1, 2, 4, 8, 16, 32):
    done = set(); ready = [f for f in files if not deps[f]]; t = 0.0; run = []; left = {f: len(deps[f]) for f in files}
    ready = [(-bl[f], f) for f in ready]; heapq.heapify(ready)
    while ready or run:
        while ready and len(run) < J:
            _, f = heapq.heappop(ready); heapq.heappush(run, (t + T[f], f))
        t, f = heapq.heappop(run)
        for g in users[f]:
            left[g] -= 1
            if left[g] == 0: heapq.heappush(ready, (-bl[g], g))
    print('  J=%-2d wall %6.0f s  (%.1f h)' % (J, t, t / 3600))
# the critical chain
f = max((g for g in files if not deps[g]), key=lambda g: bl[g]); chain = [f]
while users[f]:
    f = max(users[f], key=lambda g: bl[g]); chain.append(f)
print('critical chain: ' + ' -> '.join('%s (%.0f)' % (g, T[g]) for g in chain))
