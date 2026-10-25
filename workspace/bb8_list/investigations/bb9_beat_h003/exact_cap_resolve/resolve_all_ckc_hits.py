import os
import subprocess
import sys

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve, classify_cell, find_period

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"
EXE = os.path.join(BASE_DIR, "strict_tables_cap.exe")
FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS

# 1. Why did rem_part1.tsv stop at 1243 rows?
with open(os.path.join(OUT_DIR, "rem_part1.tsv"), "r", encoding="utf-8") as f:
    lines1 = f.readlines()
print(f"rem_part1.tsv lines: {len(lines1)}")
print("Line 1243:", lines1[1242].strip())
if len(lines1) > 1243:
    print("Line 1244:", lines1[1243].strip())

# 2. Collect all hits from tables_clean_k_231, tables_clean_k_232, tables_rem_part1, tables_rem_part2
hits_tsv = os.path.join(OUT_DIR, "ckc_hits_all.tsv")
seen = set()
with open(hits_tsv, "w", encoding="utf-8") as fout:
    for fn in ("tables_clean_k_231.txt", "tables_clean_k_232.txt", "tables_rem_part1.txt", "tables_rem_part2.txt"):
        for cat, fam, tm, tab in load(os.path.join(OUT_DIR, fn)):
            hks = [k for k in sorted(tab) if "H" in tab[k][0]]
            if hks and tm not in seen:
                seen.add(tm)
                fout.write(f"HIT\t{fam}\t{tm}\t| k20=K\n")

print(f"Collected {len(seen)} unique CKC hits with any H in k=1..36.")

for capx in ("0", "24"):
    out_p = os.path.join(OUT_DIR, f"tables_ckc_hits_k60_cap{capx}.txt")
    with open(out_p, "w", encoding="utf-8") as fout:
        p = subprocess.Popen([EXE, hits_tsv, "1", "HIT", "60", capx], stdout=fout, stderr=subprocess.PIPE, creationflags=FLAGS)
        p.communicate()
    print(f"\n=== Results at KMAX=60, CAPX={capx} ===")
    for cat, fam, tm, tab in load(out_p):
        res, r, traj, per = solve(tab, 60)
        hks = [k for k in sorted(tab) if tab[k][0] == "HH"]
        print(f"  [{res:10s} R={r:2d}] {fam:22s} {tm} | per={per} Hk={hks[:10]} traj={traj[:6]}")
