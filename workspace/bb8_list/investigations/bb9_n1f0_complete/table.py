"""table.py: per-row markdown table from res1.tsv (graded rows) + resC.tsv (champion rows) + comp screening.
Columns: machine, grade, template, undefined, slot read (per R in 18-23), first list, growth of the cleared list
per period at R=20 (successive new maxima), completions (leaves) and their screening classes."""
import collections, re, os
def expand(z):
    v = []
    for t in z.split():
        if '^' in t:
            x, c = t.split('^'); v += [int(x)] * int(c)
        elif t:
            v.append(int(t))
    return v
def growth(v):
    mx, out = -1, []
    for x in v:
        if x > mx + 2:
            out.append(x); mx = x
        mx = max(mx, x)
    return out
comp = collections.defaultdict(collections.Counter)
if os.path.exists('comp_R20_screen.tsv'):
    pm = {}
    for l in open('comp_targets_all.tsv'):
        m = l.split('\t')[0]; pm[m] = m
    for l in open('comp_R20_screen.tsv'):
        x = l.rstrip('\n').split('\t')
        comp[x[0]][x[1]] += 1
def parent_of(child, parents):
    for p in parents:
        a, b = p.split('_'), child.split('_')
        if all(pa == pb or pa == '---' or pa[3:] == '---' and pa[:3] == pb[:3] or pa[:3] == '---' and pa[3:] == pb[3:] for pa, pb in zip(a, b)):
            return p
    return None
parents = [l.split('\t')[0] for l in open('comp_targets_all.tsv')] if os.path.exists('comp_targets_all.tsv') else []
pc = collections.defaultdict(collections.Counter)
for ch, c in comp.items():
    p = parent_of(ch, parents)
    if p:
        pc[p].update(c)
rows = collections.OrderedDict()
for fn, kind in (('res1.tsv', 'graded'), ('resC.tsv', 'champion')):
    if not os.path.exists(fn):
        continue
    for l in open(fn):
        x = l.rstrip('\n').split('\t')
        if len(x) < 11:
            continue
        m = x[0]
        r = rows.setdefault(m, dict(grade=x[1], t=x[2], und=x[3], out={}, z20=None, kind=kind))
        r['out'][int(x[5])] = x[6]
        if x[5] == '20':
            r['z20'] = expand(x[8])
print('| machine | grade | template | undef | outcome R=18..23 | 1st list | cleared-list maxima (R=20) | completions |')
print('|---|---|---|---|---|---|---|---|')
for m, r in rows.items():
    if r['kind'] == 'champion' and ',' not in r['und']:
        continue
    outs = sorted(set(r['out'].values()))
    o = ', '.join(outs) if len(outs) <= 2 else f'{len(outs)} kinds: ' + ', '.join(outs[:3])
    z = r['z20'] or []
    g = growth(z)
    gs = ' '.join(map(str, g[:6])) + (' ...' if len(g) > 6 else '')
    c = pc.get(m)
    cs = ', '.join(f'{k} {v}' for k, v in sorted(c.items())) if c else ('n/a (1 undefined slot)' if ',' not in r['und'] else '-')
    print(f"| `{m}` | {r['grade']} | `{r['t']}` | {r['und']} | {o} | {z[0] if z else '-'} | {gs} | {cs} |")
