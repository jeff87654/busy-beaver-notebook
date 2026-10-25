import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
import glob
import os

ROOT = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'

def lin(s):
    i = s.index('b')
    return int(s[:i]), int(s[i + 1:])

def parse_params(p):
    parts = [x.strip() for x in p.split('|')]
    R = {}
    R['m1'], R['c1'] = lin(parts[0].split()[1])
    r2 = parts[1].split()
    R['m2'], R['c2'] = lin(r2[1][2:])
    R['b2'] = int(r2[2][2:])
    r3 = parts[2].split()
    s = r3[1]
    i = s.index('b')
    R['m3'] = int(s[:i])
    rest = s[i + 1:-1]
    j = max(rest.rfind('+'), rest.rfind('-'))
    R['c3'], R['e3'] = int(rest[:j]), int(rest[j:])
    R['tail'] = int(r3[2].split('=')[1])
    R['a3'] = int(r3[3].split('=')[1])
    R['b3'] = int(r3[4].split('=')[1])
    R['r4'] = parts[3].split()[1]
    return R

def is_mult(R):
    m1, c1, m2, m3 = R['m1'], R['c1'], R['m2'], R['m3']
    if m1 >= 2 or m2 >= 2 or m3 >= 2:
        return True
    if m1 == 1 and c1 >= 2 and m2 >= 1:
        return True
    return False

files = sorted(glob.glob(os.path.join(ROOT, 'dl2_out', 'c*.tsv')))
for extra in [
    os.path.join(ROOT, 'prefilter', 'hits_dl2_1M.tsv'),
    os.path.join(ROOT, 'sample1pct', 'hits.tsv'),
    os.path.join(ROOT, 'rank', 'rows_all.tsv'),
]:
    if os.path.exists(extra):
        files.append(extra)

print(f"Scanning {len(files)} files...")
seen = {}
by_grade = {}
mult_rows = []

for fn in files:
    with open(fn, encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('#') or line.startswith('machine\t'):
                continue
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 6:
                continue
            m, hstep, n_tmpl, grade, tmpl, params = parts[:6]
            if grade == '-':
                continue
            by_grade[grade] = by_grade.get(grade, 0) + 1
            if m in seen:
                continue
            try:
                R = parse_params(params)
            except Exception as e:
                continue
            seen[m] = (grade, tmpl, params, os.path.basename(fn))
            if is_mult(R):
                mult_rows.append((m, grade, tmpl, params, os.path.basename(fn), R))

print("Total unique graded machines:", len(seen))
print("Multiplicative machines:", len(mult_rows))
from collections import Counter
print("Multiplicative by grade:", Counter(x[1] for x in mult_rows))

with open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\mult_all.tsv', 'w', encoding='utf-8') as out:
    for m, grade, tmpl, params, src, R in mult_rows:
        out.write(f"{m}\t0\t1\t{grade}\t{tmpl}\t{params}\t{src}\n")
        print(f"{grade:12s} {m} | {src:15s} | {tmpl:40s} | {params}")
