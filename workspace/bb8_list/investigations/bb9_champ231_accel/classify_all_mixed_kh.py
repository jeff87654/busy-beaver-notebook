import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter, defaultdict
from solve_multiround import load_tsv
from verify_rule_d import parse_tm

for label, path in [
    ("champ_231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
    ("champ_232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
]:
    rows, _ = load_tsv(path)
    mixed = [(tm, cells) for tag, tm, cells in rows if tag == "MIXED_KH"]
    k20_counts = Counter(cells[20]['kind'] for _, cells in mixed)
    print(f"================ {label}: {len(mixed)} MIXED_KH rows ================")
    print("k20 outcome distribution:", dict(k20_counts))

    # Group all MIXED_KH where k20 == 'T' AND at least one of k=4..9 is K or K*
    late_k_patterns = Counter()
    late_k_ex = {}
    for tm, cells in mixed:
        if cells[20]['kind'] == 'T' and any(cells[k]['kind'] in ('K', 'K*') for k in range(4, 10)):
            pf = ",".join(cells[k]['kind'] for k in range(1, 10))
            late_k_patterns[pf] += 1
            if pf not in late_k_ex:
                late_k_ex[pf] = (tm, cells)

    print(f"\nMIXED_KH patterns with k20=T and K/K* in k=4..9 ({sum(late_k_patterns.values())} total):")
    for pf, cnt in late_k_patterns.most_common(30):
        tm, cells = late_k_ex[pf]
        c_str = ",".join(str(cells[k]['c']) for k in range(1, 10))
        print(f"  cnt={cnt:3d} | {pf:26s} | c1..9=[{c_str}] | ex={tm}")
