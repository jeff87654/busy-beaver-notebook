import os

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"

for name, has_fam, cats in [
    ("std9_exact_231.tsv", False, {"CLEAN_K", "CASCADE"}),
    ("std9_exact_232.tsv", False, {"CLEAN_K", "CASCADE"}),
    ("search_arch_a_d.tsv", True, {"K_CASCADE"}),
]:
    total_k20K = 0
    no_T = 0
    low_clears = 0
    with open(os.path.join(BASE_DIR, name), "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "| k20=K" not in line:
                continue
            parts = line.split()
            if parts[0] not in cats:
                continue
            total_k20K += 1
            if "=T(" not in line:
                no_T += 1
                # check if c count at k20 is < 100 (otherwise it exceeds 80000 steps in strict_tables_cap)
                k20_part = line.split("| k20=")[1].split()[0]
                if ",c" in k20_part:
                    c_val = int(k20_part.split(",c")[1].split(")")[0])
                    if c_val < 100:
                        low_clears += 1
                else:
                    low_clears += 1
    print(f"{name:22s}: total_k20K={total_k20K}, no_T={no_T}, no_T_and_c<100={low_clears}")
