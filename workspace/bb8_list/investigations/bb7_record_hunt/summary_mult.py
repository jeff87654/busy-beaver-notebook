import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
from collections import Counter

rows = [line.rstrip('\n').split('\t') for line in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\mult_all.tsv')]
target_grades = {'HALT-SOME', 'CHECK', 'NOBOUNDARY', 'HALT?'}
trows = [r for r in rows if r[3] in target_grades]
print("Target multiplicative rows:", len(trows))

# Group by (grade, R4, P)
def get_r4(params):
    for p in params.split('|'):
        p = p.strip()
        if p.startswith('R4 '):
            return p.split()[1]
    return '?'

def get_P(tmpl):
    for x in tmpl.split(','):
        if x.startswith('P='):
            return x[2:]
    return '?'

c = Counter((r[3], get_r4(r[5]), get_P(r[4]) != '-') for r in trows)
for k, v in sorted(c.items()):
    print(f"grade={k[0]:12s} R4={k[1]:6s} P_nonempty={str(k[2]):5s} : {v}")
