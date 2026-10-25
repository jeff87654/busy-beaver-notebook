"""pool.py: assemble the reb7 pool -> pool7.tsv (machine, template, grade, sources, cls class/growth)."""
import idle  # noqa
B = r'C:\Users\jeffr\Downloads\bb8'
SRC = [('dl3_hits', B + r'\bb7_holdouts\dl3_hits\out.tsv'), ('dl3_triage7', B + r'\bb7_holdouts\dl3_triage7\out.tsv'),
       ('dl3_c', B + r'\bb7_holdouts\reb7\dl3_c.tsv'),
       ('triage7_1RB1LA', B + r'\bb8_list\investigations\bb9_triage7_and_1RB1LA\new_dl3_out.tsv')]
GR = ['W1-HALTER=0', 'W1-LOOPER', 'MULTI', 'MULTI?', 'LOOPER', 'REBUILD', 'CHAMPION', 'R4-SOME', 'HALT-SOME', 'HALT?',
      'NOBOUNDARY']
cls = {}
for l in open(B + r'\bb8_list\investigations\bb9_fw1_hosts\cls_all.tsv'):
    f = l.rstrip('\n').split('\t')
    if len(f) > 5 and f[1] == '7':
        cls[f[0]] = f[4] + '/' + f[5]
rows = {}
for tag, fn in SRC:
    for l in open(fn, errors='ignore'):
        f = l.rstrip('\n').split('\t')
        if len(f) < 5 or f[0] == 'machine' or len(f[0]) != 48:
            continue
        if f[3] not in GR:
            continue
        r = rows.setdefault(f[0], {'t': f[4], 'g': f[3], 'src': []})
        r['src'].append(tag)
        if GR.index(f[3]) < GR.index(r['g']):
            r['g'], r['t'] = f[3], f[4]
with open('pool7.tsv', 'w', newline='\n') as fo:
    fo.write('machine\ttemplate\tgrade\tsources\tcls\n')
    order = sorted(rows, key=lambda m: (GR.index(rows[m]['g']), m))
    for m in order:
        r = rows[m]
        fo.write('%s\t%s\t%s\t%s\t%s\n' % (m, r['t'], r['g'], ','.join(r['src']), cls.get(m, '-')))
from collections import Counter
print(len(rows), Counter(r['g'] for r in rows.values()))
print('cls7 missing from pool:', len(set(cls) - set(rows)))
