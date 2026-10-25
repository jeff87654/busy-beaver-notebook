import os
import subprocess
import sys

sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import load, solve

BASE_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003"
OUT_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"
EXE = os.path.join(BASE_DIR, "strict_tables_cap.exe")
FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS

with open(os.path.join(OUT_DIR, "rem_part1.tsv"), "r", encoding="utf-8") as f:
    lines1 = f.readlines()

# Resume from 1243 to end, skipping any single crashing line automatically
idx = 1243
out_all = os.path.join(OUT_DIR, "tables_rem_part1_rest.txt")
crashed = []
with open(out_all, "w", encoding="utf-8") as fout:
    while idx < len(lines1):
        tmp_in = os.path.join(OUT_DIR, "tmp_rem1.tsv")
        tmp_out = os.path.join(OUT_DIR, "tmp_rem1.out")
        with open(tmp_in, "w", encoding="utf-8") as ft:
            ft.writelines(lines1[idx:])
        with open(tmp_out, "w", encoding="utf-8") as fo:
            p = subprocess.Popen([EXE, tmp_in, "1", "REM_CKC", "36", "0"], stdout=fo, stderr=subprocess.PIPE, creationflags=FLAGS)
            p.communicate()
        with open(tmp_out, "r", encoding="utf-8") as fo:
            done_lines = [l for l in fo if l.strip()]
        fout.writelines(done_lines)
        fout.flush()
        idx += len(done_lines)
        if idx < len(lines1):
            crashed.append((idx, lines1[idx].strip()))
            print(f"Skipped crashing row at idx={idx}: {lines1[idx].strip()}")
            idx += 1

print(f"Completed remaining rows of rem_part1.tsv! Total crashed={len(crashed)}")
rows = load(out_all)
rows_h = []
for cat, fam, tm, tab in rows:
    res_s, r, traj, per = solve(tab, max(tab))
    hks = [k for k in sorted(tab) if "H" in tab[k][0]]
    if hks:
        rows_h.append((res_s, r, fam, tm, per, hks, tab))
print(f"=== tables_rem_part1_rest.txt: {len(rows)} rows, {len(rows_h)} with any H/h in k=1..36 ===")
for res_s, r, fam, tm, per, hks, tab in rows_h:
    print(f"  [{res_s:10s} R={r}] {fam:18s} {tm} | per={per} Hk={hks}")
