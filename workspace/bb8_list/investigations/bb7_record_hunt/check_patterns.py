import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
from collections import Counter
import subprocess

# Re-run scan_holdouts first
import scan_holdouts

rows = [line.rstrip('\n').split('\t') for line in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\mult_all.tsv')]
ps = Counter()
for r in rows:
    t = r[4].split(',')
    kv = {x.split('=')[0]: x.split('=')[1] for x in t[2:]}
    ps[(kv['P'], kv['u'], kv['s'], kv['d'])] += 1

print("\nDistinct (P, u, s, d) patterns across multiplicative rows:")
for (P, u, s, d), cnt in ps.most_common():
    print(f"  P={P:10s} u={u:6s} s={s:6s} d={d:6s} : {cnt}")
