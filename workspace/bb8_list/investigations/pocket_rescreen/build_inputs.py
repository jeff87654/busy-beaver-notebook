"""build_inputs.py: rank_in.tsv (dl2 format) for rank7 and pool_in.tsv (machine, template, tag) for reb7.
v1 dlscan keys O,state,suffix,unit,sep become O,state,P=-,u=unit,s=sep,d=1d+0,b=1b+0,S=suffix."""
import re
B = r'C:\Users\jeffr\Downloads\bb8\bb8_list'
DUMMY = 'R1 1b+2 | R2 a=1b+2 b=0 | R3 1b+2+0k tail=0 a=0 b=0 | R4 ----- | H -'
rows = [l.rstrip('\n').split('\t') for l in open('have_dl2.tsv')]
need = set(l.strip() for l in open('need_grade.txt') if l.strip())
def v1conv(key):
    f = key.strip().split(',')
    if len(f) != 5: return None
    o, q, suf, u, s = f
    return '%s,%s,P=-,u=%s,s=%s,d=1d+0,b=1b+0,S=%s' % (o, q, u, s, suf if suf else '-')
v1 = {}
srcfiles = [(B + r'\neighbors\dl_hits.tsv', 3, 7, 5, 4), (B + r'\investigations\champ12_subtree\roots_grade\dl.tsv', 0, 3, None, 1)]
for fn, mi, di, gi, vi in srcfiles:
    for l in open(fn, encoding='utf-8', errors='replace'):
        f = l.rstrip('\n').split('\t')
        if len(f) <= di or f[mi] not in need or f[mi] in v1: continue
        keys = re.split(r'\s*\|\|\s*|;', f[di])
        for k in keys:
            m = re.match(r'([LR],[A-H],[01]*,[01]+,[01]+)(?:\s*\[(\w[\w?-]*)\])?', k.strip())
            if m:
                g = m.group(2) or (f[vi] if vi is not None else 'PARTIAL')
                t = v1conv(m.group(1))
                if t: v1[f[mi]] = (t, 'V1-' + g.replace('DIGIT-LIST', 'DL'))
                break
for m, (t, g) in sorted(v1.items()):
    rows.append([m, '-1', '0', g, t, DUMMY])
grades = sorted(set(r[3] for r in rows))
with open('rank_in.tsv', 'w', newline='\n') as o:
    for r in rows: o.write('\t'.join(r) + '\n')
with open('pool_in.tsv', 'w', newline='\n') as o:
    for r in rows: o.write('%s\t%s\t%s\tpocket\t-\n' % (r[0], r[4], r[3]))
print(len(rows), 'rows;', len(v1), 'v1-converted; missing v1:', len(need - set(v1)))
print(','.join(grades))
