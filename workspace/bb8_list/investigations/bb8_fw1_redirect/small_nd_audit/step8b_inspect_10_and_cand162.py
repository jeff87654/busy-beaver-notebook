import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

# Load noinv_blank.tsv
noinv_blank = {}
with open(os.path.join(FW1_DIR, "noinv_blank.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            noinv_blank[p[1]] = (p[0], p[2], int(p[3]), int(p[4]), int(p[5]), p[6] if len(p) > 6 else "")

ten_leaves = [
    ("e", "A01R", "1RH1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_---0RA_1LB0LG"),
    ("e", "A01R", "1RH1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_---0RA_0LD0LG"),
    ("e", "A01L", "1LH1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_---0RA_0LF0RH"),
    ("g", "A01R", "1RH1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_---0RA_1LB0LG"),
    ("g", "A01R", "1RH1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_---0RA_0LD0LG"),
    ("g", "A01L", "1LH1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_---0RA_0LF0RH"),
    ("h", "G01L", "1RB1RA_0RC0RA_0LD1RC_0LE1LE_---1LF_1RA0LG_1LH1LG_1RB0RF"),
    ("p", "C01L", "1RB1LA_1LC1RE_1LH1RC_0LA0LG_1LD0RF_---0RC_1LE1LG_0LG0RH"),
    ("q", "C01L", "1RB1LA_1RC1RE_1LH1RC_0LA0LG_1LD0RF_---0RC_1LE1LG_0LG0RH"),
    ("u", "B01R", "1RB1RE_1RH1RB_0LD0LG_0RA1LD_---1RF_1LG0RB_1LC1LG_1LC0LF"),
]

print("=== 1. Blank trace and D/B1/LB1 of the 10 newly found E-halting leaves ===")
for tag, slot, m in ten_leaves:
    b = noinv_blank.get(m)
    B0 = BASES[tag][2]
    tt = T(tag)
    cfgs = [([2, 3], a) for a in range(1, 5)] + [([2, 2, 0], a) for a in range(3, 7)] + [([1, 0], a) for a in range(3, 7)]
    sf = os.path.join(WORKDIR, "tmp_starts_8b.txt")
    with open(sf, "w") as f:
        for i, (ds, a) in enumerate(cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_8b.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "100000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    pcols = res.stdout.strip().split("\t")[1:]
    print(f"  [{tag}] {slot} {m} | blank={b}")
    print(f"    D(1..4)={pcols[:4]} | B1(3..6)={pcols[4:8]} | LB1(3..6)={pcols[8:12]}")

# 2. Also run kblank_detail.exe up to 10M steps on these 10 leaves!
exe_file = os.path.join(WORKDIR, "kblank_detail.exe")
print("\n=== 2. Running 10M-step kblank_detail on the 10 leaves ===")
for tag, slot, m in ten_leaves:
    B0 = BASES[tag][2]
    mf = os.path.join(WORKDIR, "tmp_probe_8b.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [exe_file, mf] + targs(tag) + ["10000000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    print(f"  [{tag}] {res.stdout.strip()}")

# 3. Check cand162.tsv against probe_919.tsv and noinv_leaves.txt!
print("\n=== 3. Checking cand162.tsv ===")
cand162 = []
with open(os.path.join(FW1_DIR, "cand162.tsv")) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            cand162.append((p[0], p[1], p[2], p[3:]))
print(f"Total rows in cand162.tsv: {len(cand162)}")
in_noinv = set()
with open(os.path.join(FW1_DIR, "noinv_leaves.txt")) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            in_noinv.add(p[0])
overlap = sum(1 for _, _, m, _ in cand162 if m in in_noinv)
print(f"cand162 overlap with noinv_leaves.txt: {overlap}")
