import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

# 1. Check 1-digit configs [3]; 11, [2]; 24, [1]; 51, []; 104 on the 3 [s] leaves
tag = "s"
B0 = BASES[tag][2]
tt = T(tag)
cfgs = [
    ("[3];11", [3], 11),
    ("[2];12", [2], 12),
    ("[2];24", [2], 24),
    ("[1];11", [1], 11),
    ("[1];12", [1], 12),
    ("[];12", [], 12),
    ("[];24", [], 24),
]
sf = os.path.join(WORKDIR, "tmp_3s_starts.txt")
with open(sf, "w") as f:
    for i, (lbl, ds, a) in enumerate(cfgs):
        w = word(tag, ds, a, B0)
        f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")

mlist = [
    "0LH0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG_1RG1RH",
    "1LH0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG_0RB1LG",
    "1LH0LG_1RC1RB_0RD0RB_0LE1RD_0LE1LF_---1LA_1LC1LG_0RB1RG",
]
mf = os.path.join(WORKDIR, "tmp_3s_mlist.txt")
with open(mf, "w") as f:
    for m in mlist:
        f.write(m + "\n")

cmd = [kmap2_exe, mf] + targs(tag) + [sf, "100000", str(B0)]
res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
for m, line in zip(mlist, res.stdout.strip().split("\n")):
    pcols = line.split("\t")[1:]
    print(f"[s] {m}:")
    for (lbl, _, _), o in zip(cfgs, pcols):
        print(f"  {lbl:8s} -> {o}")

# 2. Check E(3), E(6), E(9), E(12), E(15), E(18), LB2(5..6) on the 8 [e, g] leaves
for tag in ("e", "g"):
    B0 = BASES[tag][2]
    tt = T(tag)
    cfgs_eg = [(f"E({a})", [], a) for a in (3, 6, 9, 12, 15, 18)] + [
        ("LB1(5)", [1, 0], 5),
        ("LB1(6)", [1, 0], 6),
        ("LB2(5)", [1, 0, 0], 5),
        ("LB2(6)", [1, 0, 0], 6),
    ]
    sf = os.path.join(WORKDIR, f"tmp_eg_starts_{tag}.txt")
    with open(sf, "w") as f:
        for i, (lbl, ds, a) in enumerate(cfgs_eg):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    if tag == "e":
        ms = [
            "1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_0RF0RH_---0RA",
            "1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RG_1LE1LF_1LE0RH_---0RA",
            "1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RH_1LE1LF_---0RA_0RF0RG",
            "1RB1RA_0LC0LF_1RD1LC_1LA1RE_1LB0RH_1LE1LF_---0RA_1LE0RG",
        ]
    else:
        ms = [
            "1RB1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_0RF0RH_---0RA",
            "1RB1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RG_1LE1LF_1LE0RH_---0RA",
            "1RB1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RH_1LE1LF_---0RA_0RF0RG",
            "1RB1RA_0LC0LF_1RD1LC_1RA1RE_1LB0RH_1LE1LF_---0RA_1LE0RG",
        ]
    mf = os.path.join(WORKDIR, f"tmp_eg_mlist_{tag}.txt")
    with open(mf, "w") as f:
        for m in ms:
            f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "100000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    for m, line in zip(ms, res.stdout.strip().split("\n")):
        pcols = line.split("\t")[1:]
        print(f"[{tag}] {m}: {[f'{lbl}={o}' for (lbl,_,_), o in zip(cfgs_eg, pcols)]}")
