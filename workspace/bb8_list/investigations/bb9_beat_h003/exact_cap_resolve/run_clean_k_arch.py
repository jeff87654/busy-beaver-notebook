import os

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
ACCEL_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel"

for name, path, has_fam in [
    ("std9_exact_231.tsv", os.path.join(BASE_DIR, "std9_exact_231.tsv"), False),
    ("std9_exact_232.tsv", os.path.join(BASE_DIR, "std9_exact_232.tsv"), False),
    ("search_arch_a_d.tsv", os.path.join(BASE_DIR, "search_arch_a_d.tsv"), True),
    ("accel_champ231_9.tsv", os.path.join(ACCEL_DIR, "accel_champ231_9.tsv"), False),
    ("accel_champ232_9.tsv", os.path.join(ACCEL_DIR, "accel_champ232_9.tsv"), False),
]:
    counts = {}
    counts_halt_trans = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "| k20=K" not in line:
                continue
            parts = line.split()
            cat = parts[0]
            tm = parts[2] if has_fam else parts[1]
            counts[cat] = counts.get(cat, 0) + 1
            if "---" in tm:
                counts_halt_trans[cat] = counts_halt_trans.get(cat, 0) + 1
    print(f"{name:22s} | k20=K all: {counts} | with '---': {counts_halt_trans}")
