import sys; sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts'); import idle

rows = [line.rstrip('\n').split('\t') for line in open(r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb7_record_hunt\mult_all.tsv')]
print("=== HALT-SOME or R4 contains T ===")
for r in rows:
    if r[3] == 'HALT-SOME' or ('T' in r[5].split('|')[3]):
        print(f"{r[3]:12s} {r[0]} | {r[6]:12s} | {r[4]:42s} | {r[5]}")
