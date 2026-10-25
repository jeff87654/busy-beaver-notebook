import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from analyze_arch_a_d import load_tsv, detect_period_rule_gen, trace_blank_tape_rounds, MOD, THREE_A_MOD

for label, path, has_fam in [
    ("search_arch_a_d", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\search_arch_a_d.tsv", True),
    ("accel_champ231_9", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv", False),
    ("accel_champ232_9", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv", False),
]:
    rows, _ = load_tsv(path, has_fam=has_fam)
    print(f"=== Scanning {label} ({len(rows)} rows) ===")
    for tag, fam, tm, ec_s, cells in rows:
        if "1LG---" in tm and "1LH" in tm:
            pf = ",".join(f"{cells[k]['kind']}" for k in range(1, 10))
            print(f"  [1LG--- match] {fam:20s} {tm} | {pf} | k20={cells[20]['kind']}")
        # Try ALL k_start in 1..5 without breaking early if status != HALT!
        best_r = -1
        best_info = None
        for k_start in [1, 2, 3, 4, 5]:
            P, rules = detect_period_rule_gen(cells, k_start=k_start, max_P=6)
            if P is not None and any(v[0] == 'H' for v in rules.values()) and any(v[0] == 'K' for v in rules.values()):
                status, r_end, hist = trace_blank_tape_rounds(P, rules, max_rounds=30)
                if status == 'HALT' and r_end > best_r:
                    best_r = r_end
                    best_info = (k_start, P, rules, hist)
        if best_r >= 4:
            k_start, P, rules, hist = best_info
            pf = ",".join(f"{cells[k]['kind']}" for k in range(1, 10))
            h_str = " ; ".join(f"R{r}:(k%12={km%12},I={ic})->{act}{extra}" for r, km, ic, act, extra in hist)
            print(f"  *** HALT @ R{best_r:2d} (k_start={k_start}, P={P}) {fam:20s} {tm} | {pf} | {h_str}")
