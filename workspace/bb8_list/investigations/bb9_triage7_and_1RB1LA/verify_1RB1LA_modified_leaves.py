import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle

HERE = os.path.dirname(os.path.abspath(__file__))
tsv_path = os.path.join(HERE, 'henum_1RB1LA_9.tsv')
with open(tsv_path, 'r', encoding='utf-8') as f:
    lines = [l.rstrip('\r\n') for l in f if l.strip() and not l.startswith('#')]

partial_r4 = []
r4_r2_halts = []
big_maxW = []

for l in lines:
    parts = l.split('\t')
    tag, m, b_info, r1_info, r3a_info = parts[0], parts[1], parts[2], parts[3], parts[4]
    r4_infos = parts[5:11]
    r4_r2 = parts[11] if len(parts) > 11 else ""
    r4_kinds = [x.split('=')[1][0] for x in r4_infos]
    if 'H' in r4_kinds and 'K' in r4_kinds:
        partial_r4.append(parts)
    if '=H:' in r4_r2:
        r4_r2_halts.append(parts)
    for tok in b_info.split(':'):
        if tok.startswith('maxW='):
            mw = int(tok.split('=')[1])
            if mw >= 20:
                big_maxW.append((mw, parts))

print("=== Checking mixed R4(b) leaves ===")
for p in partial_r4[:10]:
    print("  ", p[0], p[1], p[2], p[3], p[4], " ".join(p[5:9]))

print("\n=== Checking Round-2 R4 halt leaves ===")
for p in r4_r2_halts[:10]:
    print("  ", p[0], p[1], p[2], p[3], p[4], p[11])

print("\n=== Checking big maxW leaves ===")
for mw, p in sorted(big_maxW, reverse=True)[:10]:
    print(f"  maxW={mw}:", p[0], p[1], p[2], p[3], p[4])
