import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from collections import Counter, defaultdict
from analyze_accel_results import load_tsv

for label, path in [
    ("champ_231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv"),
    ("champ_232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv"),
]:
    rows, _ = load_tsv(path)
    print(f"================ {label}: ALL ZERO-TIMEOUT MIXED_KH PATTERNS ================")
    pat_c = Counter()
    pat_ex = {}
    for tag, tm, cells in rows:
        if tag != "MIXED_KH": continue
        kinds = [cells[k]['kind'] for k in range(1, 10)]
        if 'T' in kinds: continue
        k20 = cells[20]['kind']
        key = (tuple(kinds), k20)
        pat_c[key] += 1
        if key not in pat_ex:
            pat_ex[key] = (tm, cells)
    for (kinds, k20), cnt in pat_c.most_common(50):
        tm, cells = pat_ex[(kinds, k20)]
        pf = ",".join(kinds)
        c_str = ",".join(str(cells[k]['c']) for k in range(1, 10))
        s_str = ",".join(str(cells[k]['step']) for k in range(1, 7))
        print(f"  cnt={cnt:3d} | {pf:26s} | k20={k20:2s} | c=[{c_str}] | s1..6=[{s_str}] | {tm}")
