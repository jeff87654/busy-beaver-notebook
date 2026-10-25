import sys, idle_guard
from fam import *
rows = [[0, l.strip()] for l in open("reps.txt") if l.strip()]
extra = ['1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1LA0LG_1LB1LG', '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE',
         '1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA']
done = set()
try: done = set(l.split('\t')[0] for l in open('detect2.tsv'))
except: pass
with open('detect2.tsv', 'a') as f:
    for m in [r[1] for r in rows]:
        if m in done: continue
        try: d = detect2(m, 1500000)
        except Exception as ex: d = None
        if d is None: f.write('%s\t-\n' % m)
        else: f.write('%s\t%s\t%s\t%s\t%s\t%s\t%.3f\n' % (m, d[1], d[2], ','.join(map(str, d[3])) or '-', d[4], d[5], d[6]))
        f.flush()
