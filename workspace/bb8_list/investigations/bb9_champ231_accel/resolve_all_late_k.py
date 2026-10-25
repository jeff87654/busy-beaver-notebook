import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm
from solve_multiround import load_tsv
from test_ackermann_macro import run_ackermann_sim
from collections import Counter

def resolve_family(rows, is_232=False, label="champ_231"):
    t_rows = [(tag, tm, cells) for tag, tm, cells in rows if tag == "MIXED_KH" and cells[20]["kind"] == "T"]
    print(f"=== Resolving {len(t_rows)} MIXED_KH rows with k20=T on {label} ===")
    resolved_patterns = Counter()
    examples = {}
    for tag, tm, cells in t_rows:
        tr = parse_tm(tm)
        ks_res = []
        for k in list(range(1, 13)) + [20]:
            res = run_ackermann_sim(tr, k, 2*k + 6, is_232=is_232, max_iters=12000)
            ks_res.append((k, res[0], res[2], res[3], res[5]))
        pat = ",".join(x[1] for x in ks_res[:9])
        pat12 = ",".join(x[1] for x in ks_res[9:12])
        k20_kind = ks_res[-1][1]
        key = (pat, pat12, k20_kind)
        resolved_patterns[key] += 1
        if key not in examples:
            examples[key] = (tm, ks_res)

    for (pat, pat12, k20_kind), cnt in resolved_patterns.most_common():
        tm, ks_res = examples[(pat, pat12, k20_kind)]
        detail_str = " ".join(f"k{k}={kd}({dL},c{aj})" for k, kd, dL, pI, aj in ks_res)
        print(f"  {cnt:4d}x : k1..9={pat:24s} | k10..12={pat12:8s} | k20={k20_kind:2s} | ex: {tm}")
        print(f"          {detail_str}")

if __name__ == "__main__":
    r231, _ = load_tsv(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv")
    r232, _ = load_tsv(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv")
    resolve_family(r231, False, "champ_231")
    print()
    resolve_family(r232, True, "champ_232")
