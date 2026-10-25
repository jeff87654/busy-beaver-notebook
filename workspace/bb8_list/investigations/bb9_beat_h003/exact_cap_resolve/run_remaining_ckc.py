import os
import subprocess
import sys
import time

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve
from build_and_run_scan import has_reachable_halt

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"
EXE = os.path.join(BASE_DIR, "strict_tables_cap.exe")
FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS

already_tested = set()
for fname in (
    "tables_clean_k_231.txt",
    "tables_clean_k_232.txt",
    "tables_cascade_231.txt",
    "tables_cascade_232.txt",
):
    fpath = os.path.join(OUT_DIR, fname)
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split("\t")
                if len(parts) >= 3:
                    already_tested.add(parts[2])

rem_rows = []
for name, has_fam, cats in [
    ("std9_exact_231.tsv", False, {"CLEAN_K", "CASCADE"}),
    ("std9_exact_232.tsv", False, {"CLEAN_K", "CASCADE"}),
    ("search_arch_a_d.tsv", True, {"K_CASCADE"}),
]:
    with open(os.path.join(BASE_DIR, name), "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if "| k20=K" not in line or "=T(" in line:
                continue
            parts = line.split()
            cat = parts[0]
            if cat not in cats:
                continue
            fam = parts[1] if has_fam else "STD9"
            tm = parts[2] if has_fam else parts[1]
            if tm in already_tested or not has_reachable_halt(tm):
                continue
            k20_part = line.split("| k20=")[1].split()[0]
            if ",c" in k20_part:
                c_val = int(k20_part.split(",c")[1].split(")")[0])
                if c_val >= 80:
                    continue
            already_tested.add(tm)
            rem_rows.append(f"REM_CKC\t{fam}\t{tm}\t| k20=K\n")

print(f"Filtered fast remaining CLEAN_K/CASCADE/K_CASCADE rows: {len(rem_rows)}")
mid = len(rem_rows) // 2
p1_in = os.path.join(OUT_DIR, "rem_part1.tsv")
p2_in = os.path.join(OUT_DIR, "rem_part2.tsv")
p1_out = os.path.join(OUT_DIR, "tables_rem_part1.txt")
p2_out = os.path.join(OUT_DIR, "tables_rem_part2.txt")

with open(p1_in, "w", encoding="utf-8") as f:
    f.writelines(rem_rows[:mid])
with open(p2_in, "w", encoding="utf-8") as f:
    f.writelines(rem_rows[mid:])

t0 = time.time()
f1 = open(p1_out, "w", encoding="utf-8")
f2 = open(p2_out, "w", encoding="utf-8")
proc1 = subprocess.Popen([EXE, p1_in, "1", "REM_CKC", "36", "0"], stdout=f1, stderr=subprocess.PIPE, creationflags=FLAGS)
proc2 = subprocess.Popen([EXE, p2_in, "1", "REM_CKC", "36", "0"], stdout=f2, stderr=subprocess.PIPE, creationflags=FLAGS)
proc1.communicate()
proc2.communicate()
f1.close()
f2.close()
print(f"Finished both parts in {time.time() - t0:.1f}s")

for out_f in (p1_out, p2_out):
    rows = load(out_f)
    rows_h = []
    for cat, fam, tm, tab in rows:
        res_s, r, traj, per = solve(tab, max(tab))
        hks = [k for k in sorted(tab) if "H" in tab[k][0]]
        if hks:
            rows_h.append((res_s, r, fam, tm, per, hks, tab))
    print(f"=== {os.path.basename(out_f)}: {len(rows)} rows, {len(rows_h)} with any H/h in k=1..36 ===")
    for res_s, r, fam, tm, per, hks, tab in rows_h:
        print(f"  [{res_s:10s} R={r}] {fam:18s} {tm} | per={per} Hk={hks}")
