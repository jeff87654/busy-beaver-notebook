import sys
from collections import Counter
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

tsv = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_triage7_and_1RB1LA\enum_champ231_9.tsv'
with open(tsv) as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

k20_clean = []
for l in lines:
    parts = l.split('\t')
    tag, tm, info = parts[0], parts[1], parts[2]
    if 'k20=K(' in info:
        toks = info.split('|')[0].strip().split()
        pat = ''.join('K' if '=K(' in t else ('H' if '=H(' in t else 'T') for t in toks)
        if 'T' in pat or 'H' in pat:
            k20_clean.append((pat, tm, info))

print(f"Total leaves with k20=K(...) AND selective (some T or H in k1..k9): {len(k20_clean)}")
pats = Counter(p[0] for p in k20_clean)
for pat, cnt in pats.most_common(40):
    ex = next(p for p in k20_clean if p[0] == pat)
    print(f"  {pat} ({cnt:4d}x): {ex[1]} | {ex[2]}")
