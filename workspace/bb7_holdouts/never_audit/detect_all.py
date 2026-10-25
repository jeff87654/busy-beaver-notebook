import sys, idle_guard
from fam import *
rows = [l.rstrip('\n').split('\t') for l in open('targets0.tsv')]
extra = ['1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LA0LG_1LB1LG', '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE']
done = set()
try: done = set(l.split('\t')[0] for l in open('detect.tsv'))
except: pass
with open('detect.tsv', 'a') as f:
    for m in [r[1] for r in rows] + extra:
        if m in done: continue
        try: d = detect(m)
        except Exception as ex: d = None
        if d is None: f.write('%s\t-\n' % m)
        else: f.write('%s\t%s\t%s\t%s\t%s\t%.3f\n' % (m, d[1], d[2], ','.join(map(str, d[3])) or '-', d[4], d[5]))
        f.flush()
