import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

tsv = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_triage7_and_1RB1LA\enum_champ231_9.tsv'
with open(tsv) as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

print(f"Total lines in enum_champ231_9.tsv: {len(lines)}")
mixed = [l for l in lines if l.startswith('MIXED_KH')]
print(f"Total MIXED_KH lines: {len(mixed)}")

# Group by pattern of (k1..k9, k20)
k20_is_K_and_has_H = []
periodic_kh = []

for l in mixed:
    parts = l.split('\t')
    tag, tm, info = parts[0], parts[1], parts[2]
    if 'k20=K(' in info:
        k20_is_K_and_has_H.append((tm, info))
    # Also check how many k in 1..9 are K vs H
    toks = info.split('|')[0].strip().split()
    pat = ''.join('K' if '=K(' in t else ('H' if '=H(' in t else 'T') for t in toks)
    periodic_kh.append((pat, tm, info))

print(f"\n=== 1. MIXED_KH leaves where k20 = K(...) (rebuilds at k=20 AND halts at some k!): {len(k20_is_K_and_has_H)} ===")
for tm, info in k20_is_K_and_has_H[:40]:
    print(f"  {tm} | {info}")

print("\n=== 2. Distinct (k1..k9) K/H/T patterns among all 343 MIXED_KH leaves ===")
from collections import Counter
pats = Counter(p[0] for p in periodic_kh)
for pat, cnt in pats.most_common(40):
    ex = next(p for p in periodic_kh if p[0] == pat)
    print(f"  {pat} ({cnt:3d}x): {ex[1]} | {ex[2]}")
