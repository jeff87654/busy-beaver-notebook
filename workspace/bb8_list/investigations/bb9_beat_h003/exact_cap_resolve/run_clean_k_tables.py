import subprocess, time, os, sys
sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")

FLAGS = 0x08000000 | 0x40  # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS
EXE = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\strict_tables_cap.exe"
OUTDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\exact_cap_resolve"

jobs = [
    ("231", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ231_9.tsv", "0"),
    ("232", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_champ231_accel\accel_champ232_9.tsv", "0"),
    ("vsa", r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003\verify_strict_all.out.txt", "1"),
]

for tag, in_path, has_fam in jobs:
    out_path = os.path.join(OUTDIR, f"tables_clean_k_{tag}.txt")
    t0 = time.time()
    with open(out_path, "w", encoding="utf-8") as out_f:
        proc = subprocess.run(
            [EXE, in_path, has_fam, "CLEAN_K", "36", "0"],
            stdout=out_f,
            stderr=subprocess.PIPE,
            creationflags=FLAGS,
            check=True,
        )
    dt = time.time() - t0
    # Count rows and any row with H or h at any k
    rows = 0
    with_H = 0
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            rows += 1
            if ":H" in line or ":h" in line or "H:" in line or "h:" in line:
                with_H += 1
                print(f"  [{tag}] Row with H: {line.strip()[:160]}")
    print(f"Finished {tag} in {dt:.2f}s: {rows} CLEAN_K rows, {with_H} rows containing H/h in k=1..36")
