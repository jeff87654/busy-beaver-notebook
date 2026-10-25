import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle
from collections import Counter

rows = [line.rstrip('\n').split('\t') for line in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\mult_all.tsv')]
has_halt = [r for r in rows if '---' in r[0]]
no_halt = [r for r in rows if '---' not in r[0]]
print(f"Total mult: {len(rows)}, with ---: {len(has_halt)}, without ---: {len(no_halt)}")
print("With --- by grade:", Counter(r[3] for r in has_halt))
print("Without --- by grade:", Counter(r[3] for r in no_halt))
for r in has_halt:
    if r[3] not in ('CHAMPION', 'R4-SOME'):
        print(f"{r[3]:12s} {r[0]} | {r[6]:15s} | {r[4]:40s} | {r[5]}")
