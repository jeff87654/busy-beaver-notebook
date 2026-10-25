"""inventory.py: union of 8-state graded rows from the never-size-ranked pockets; dedupe vs rank8/pool8.
Outputs: inv_all.tsv (machine, sources, grades), have_dl2.tsv (dl2-format rows, latest grade), need_grade.txt."""
import re, glob, os
B = r'C:\Users\jeffr\Downloads\bb8'
CS = B + r'\bb8_list\investigations\champ12_subtree'
NB = B + r'\bb8_list\neighbors'
MRE = re.compile(r'^(?:[01-][LR-][A-H-]){2}(?:_(?:[01-][LR-][A-H-]){2}){7}$')
srcs = {}   # machine -> list of (source, grade)
dl2 = {}    # machine -> dl2-format row (machine, hs, nt, grade, template, params)
def add(m, s, g):
    if MRE.match(m): srcs.setdefault(m, []).append((s, g))
def rd(fn):
    return [l.rstrip('\n').split('\t') for l in open(fn, encoding='utf-8', errors='replace') if l.strip()]
# dl2-format files (machine, halted_step, n_templates, grade, template, params)
for fn, tag in [(CS + r'\roots_grade\dl2.tsv', 'roots_dl2'), (CS + r'\m8\dl2.tsv', 'm8_dl2'),
                (CS + r'\m8_interim_dl2.tsv', 'm8int_dl2'),
                (B + r'\bb8_list\investigations\nested_detector\scans\bb8_sample\dl2fits27_dl3.tsv', 'nest_dl3')]:
    if not os.path.exists(fn): continue
    for f in rd(fn):
        if len(f) >= 6 and MRE.match(f[0]):
            add(f[0], tag, f[3])
            p = f[6] if tag == 'nest_dl3' and len(f) > 6 else f[5]
            dl2.setdefault(f[0], [f[0], f[1], f[2], f[3], f[4], p])
for w in sorted(glob.glob(CS + r'\*\watch_hits*.tsv')):
    tag = 'watch_' + os.path.basename(os.path.dirname(w))
    for f in rd(w):
        if len(f) >= 4 and MRE.match(f[1]):
            add(f[1], tag, f[0]); dl2.setdefault(f[1], [f[1], '-1', '0', f[0], f[2], f[3]])
for f in rd(NB + r'\dl2_hits.tsv'):
    if len(f) >= 9 and MRE.match(f[3]):
        add(f[3], 'nb_dl2hits', f[5]); dl2.setdefault(f[3], [f[3], '-1', '0', f[5], f[7], f[8]])
for f in rd(NB + r'\dl_hits.tsv'):
    if len(f) >= 6: add(f[3], 'nb_dlhits', f[5] + '/' + f[4])
for f in rd(NB + r'\nob_screen.tsv'):
    if len(f) >= 4: add(f[0], 'nb_nobscreen', f[3])
ranked = set()
for fn in [B + r'\bb7_holdouts\rank\bb8\rank8.tsv']:
    for f in rd(fn)[1:]: ranked.add(f[1])
pool8 = set(f[0] for f in rd(B + r'\bb7_holdouts\reb7\pool8.tsv'))
with open('inv_all.tsv', 'w', newline='\n') as o:
    o.write('machine\tin_rank8\tin_pool8\thas_dl2\tsources\n')
    for m in sorted(srcs):
        o.write('%s\t%d\t%d\t%d\t%s\n' % (m, m in ranked, m in pool8, m in dl2, ';'.join('%s:%s' % x for x in srcs[m])))
new = [m for m in srcs if m not in ranked]
with open('have_dl2.tsv', 'w', newline='\n') as o:
    for m in sorted(new):
        if m in dl2: o.write('\t'.join(dl2[m]) + '\n')
with open('need_grade.txt', 'w', newline='\n') as o:
    for m in sorted(new):
        if m not in dl2: o.write(m + '\n')
from collections import Counter
c = Counter()
for m in srcs:
    for s, g in srcs[m]: c[s] += 1
print('sources', dict(c)); print('unique', len(srcs), 'in rank8', len(set(srcs) & ranked), 'in pool8', len(set(srcs) & pool8),
      'new', len(new), 'new with dl2 row', sum(m in dl2 for m in new), 'need grade', sum(m not in dl2 for m in new))
print('grades of new dl2 rows', Counter(dl2[m][3] for m in new if m in dl2))
