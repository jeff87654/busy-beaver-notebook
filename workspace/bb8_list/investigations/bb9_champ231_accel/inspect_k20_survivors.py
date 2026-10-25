import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter
from solve_multiround import load_tsv

for label, path in [
    ("champ_231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
    ("champ_232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
]:
    rows, _ = load_tsv(path)
    print(f"================ {label}: MIXED_KH with k20 in (K, K*) ================")
    for tag, tm, cells in rows:
        if tag == "MIXED_KH" and cells[20]['kind'] in ('K', 'K*'):
            pf = ",".join(cells[k]['kind'] for k in range(1, 10))
            c_str = ",".join(str(cells[k]['c']) for k in range(1, 10))
            print(f"  {tm} | {pf:24s} | k20={cells[20]['kind']}(dL={cells[20]['dL']:+d},I={cells[20]['I']},c={cells[20]['c']}) | c1..9=[{c_str}]")
