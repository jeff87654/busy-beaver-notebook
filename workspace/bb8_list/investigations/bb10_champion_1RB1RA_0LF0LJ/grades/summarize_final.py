"""Merge the grading passes (later passes override earlier ones) and summarise r10m14 and r10m13 separately.
usage: python summarize_final.py OUT.md"""
import glob
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def load(pattern):
    rows = {}
    for fn in sorted(glob.glob(os.path.join(HERE, pattern))):
        for line in open(fn, encoding='utf-8', errors='replace'):
            f = line.rstrip('\r\n').split('\t')
            if len(f) >= 2 and f[0]:
                rows[f[0].strip()] = f + [''] * (7 - len(f))
    return rows


merged = {}
for pat in ('snap1_chunk_0?.tsv', 'snap1_converted.tsv', 'p2_*.tsv', 'p3_*.tsv', 'p4_*.tsv', 'p5_*.tsv', 'p6.tsv'):
    merged.update(load(pat))


def machines(fn):
    return [l.strip() for l in open(os.path.join(HERE, fn), encoding='utf-8') if l.strip()]


def reason(n):
    for key, lab in (('R1FAIL', 'literal R1 fails'), ('R1 fails', 'literal R1 fails'),
                     ('leaves R2/R3', 'literal run leaves R2/R3'), ('grid fails', 'grid fails (R1-R3)'),
                     ('no Kd configuration', 'no Kd configuration'), ('disagrees with the fit', 'literal R4 disagrees with fit'),
                     ('R4 does not fit', 'R1-R3 hold, R4 fits no template (old pass)')):
        if key in n:
            return lab
    return re.sub(r'\d+', 'N', n)[:70]


def summary(name, ms):
    out = []
    rows = [merged.get(m) for m in ms]
    missing = sum(r is None for r in rows)
    rows = [r for r in rows if r is not None]
    out.append('**%s**: %d holdouts in the snapshot, %d graded%s.' % (name, len(ms), len(rows),
                                                                   ', %d not graded' % missing if missing else ''))
    out.append('')
    g = Counter(r[1] for r in rows)
    out += ['| grade | count |', '| --- | --- |'] + ['| %s | %d |' % (k, c) for k, c in g.most_common()] + ['']
    keys = Counter((r[1], r[2]) for r in rows if r[2] and r[1] not in ('OTHER-STRUCTURE',))
    if keys:
        out += ['Keys of the family machines that halt (f_omega^k(x), v = deepest digit, slope):', '',
                '| grade | key | count |', '| --- | --- | --- |']
        out += ['| %s | `%s` | %d |' % (k[0], k[1], c) for k, c in keys.most_common(25)] + ['']
    for gr in ('BEATS-CHAMPION?', 'EQUAL', 'EQUAL-KEY', 'R4-UNFIT', 'UNRESOLVED', 'HALTS-EARLY'):
        sel = [r for r in rows if r[1] == gr]
        if sel:
            out.append('%s (%d):' % (gr, len(sel)))
            out.append('')
            for r in sel[:30]:
                out.append('- `%s` %s %s' % (r[0], r[2], r[3][:220]))
            if len(sel) > 30:
                out.append('- ... (%d more)' % (len(sel) - 30))
            out.append('')
    oth = Counter(reason(r[3]) for r in rows if r[1] == 'OTHER-STRUCTURE')
    if oth:
        out += ['OTHER-STRUCTURE reasons:', '', '| reason | count |', '| --- | --- |']
        out += ['| %s | %d |' % (k, c) for k, c in oth.most_common()] + ['']
    nh = Counter(('cycle' if 'cycles' in r[3] else 'no-return R4 class' if 'no return' in r[3] else r[3][:60])
                 for r in rows if r[1] == 'NONHALT-PREDICTED')
    if nh:
        out += ['NONHALT-PREDICTED: ' + ', '.join('%s %d' % (k, c) for k, c in nh.most_common()), '']
    return out


lines = []
lines += summary('r10m14 (complete enumeration)', machines('r10m14_now.txt'))
m14set = set(machines('r10m14_now.txt'))
lines += summary('r10m13-only (snapshot of 2026-10-07 22:10, 19,788 holdouts of which 7,721 are the r10m14 holdouts above; '
                 'the rest)', [m for m in machines('r10m13_snap1.txt') if m not in m14set])
open(sys.argv[1], 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
