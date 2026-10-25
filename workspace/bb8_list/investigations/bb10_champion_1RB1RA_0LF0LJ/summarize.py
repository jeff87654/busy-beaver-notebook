"""Summarise r10grade TSV files: counts by grade, keys, notable rows, OTHER-STRUCTURE reasons.
usage: python summarize.py OUT.md file1.tsv [file2.tsv ...]"""
import re
import sys
from collections import Counter

out = sys.argv[1]
rows = []
for fn in sys.argv[2:]:
    for line in open(fn, encoding='utf-8', errors='replace'):
        f = line.rstrip('\n').split('\t')
        if len(f) >= 2:
            rows.append(f + [''] * (7 - len(f)))
grades = Counter(r[1] for r in rows)
lines = ['%d machines graded.' % len(rows), '', '| grade | count |', '| --- | --- |']
for g, c in grades.most_common():
    lines.append('| %s | %d |' % (g, c))
lines.append('')
keys = Counter((r[1], r[2]) for r in rows if r[2])
if keys:
    lines += ['Keys (grade, f_omega^k(x), tie-breakers):', '', '| grade | key | count |', '| --- | --- | --- |']
    for (g, k), c in keys.most_common():
        lines.append('| %s | %s | %d |' % (g, k, c))
    lines.append('')
for g in ('BEATS-CHAMPION?', 'EQUAL', 'EQUAL-KEY', 'R4-UNFIT', 'UNRESOLVED'):
    sel = [r for r in rows if r[1] == g]
    if sel:
        lines.append('%s (%d):' % (g, len(sel)))
        lines.append('')
        for r in sel[:40]:
            lines.append('- `%s` %s: %s' % (r[0], r[2], r[3][:300]))
        lines.append('')


def reason(n):
    if 'R1FAIL' in n:
        return 'literal R1 fails'
    if 'leaves R2/R3' in n:
        return 'literal run leaves R2/R3'
    if 'grid fails' in n:
        return 'literal run follows the rules, grid fails'
    if 'no Kd configuration' in n:
        return 'no Kd configuration'
    if 'disagrees with the fit' in n:
        return 'literal R4 disagrees with the fit'
    return re.sub(r'\d+', 'N', n)[:80]


oth = Counter(reason(r[3]) for r in rows if r[1] == 'OTHER-STRUCTURE')
if oth:
    lines += ['OTHER-STRUCTURE reasons:', '', '| reason | count |', '| --- | --- |']
    for k, c in oth.most_common():
        lines.append('| %s | %d |' % (k, c))
    lines.append('')
nh = Counter(re.sub(r'b = \d+', 'b = N', r[3].split(';')[0]) for r in rows if r[1] == 'NONHALT-PREDICTED')
if nh:
    lines += ['NONHALT-PREDICTED reasons:', '', '| reason | count |', '| --- | --- |']
    for k, c in nh.most_common():
        lines.append('| %s | %d |' % (k, c))
    lines.append('')
open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
