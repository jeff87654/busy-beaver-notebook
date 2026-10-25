import os, sys, subprocess

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

def probe_ab(tag, m, cfgs_ab, max_steps=200000):
    tt = T(tag)
    sf = os.path.join(WORKDIR, "tmp_starts_x.txt")
    with open(sf, "w") as f:
        for i, (ds, a, b) in enumerate(cfgs_ab):
            w = word(tag, ds, a, b)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, "tmp_probe_x.txt")
    with open(mf, "w") as f:
        f.write(m + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, str(max_steps), "-1"]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    out = res.stdout.strip().split("\t")[1:]
    return list(zip(cfgs_ab, out))

samples = [
    ("G#25", "d", "1RB1RA_0LC0LF_1RD1LC_0RF1RE_1LH0RG_1LE1LF_---0RA_1RG1LB"),
    ("G#27", "d", "1RB1RA_0LC0LF_1RD1LC_1LH1RE_1LB0RG_1LE1LF_---0RA_1RG1LD"),
    ("G#23", "d", "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RD"),
    ("G#24", "d", "1RB1RA_0LC0LF_0RH1LC_0RF1RE_1LB0RG_1LE1LF_---0RA_1RG1RE"),
    ("G#44", "n", "1RB1LH_0RC1RD_1LD1LC_1LE0RF_0LA0LC_---0RG_1RE1RG_0RB1LA"),
]

for name, tag, m in samples:
    print(f"=== {name} [{tag}] {m} ===")
    cfgs = []
    for ds in [[2, 3], [2, 2, 0], [1, 0], []]:
        for a in [0, 1, 2, 3]:
            for b in [0, 1, 2, 3, 4]:
                if ds == [] and a == 0 and b == 0:
                    continue
                cfgs.append((ds, a, b))
    res = probe_ab(tag, m, cfgs)
    for ds in [[2, 3], [2, 2, 0], [1, 0], []]:
        print(f"  ds={ds}:")
        for a in [0, 1, 2, 3]:
            row = [f"b={b}:{ans}" for ((d_, a_, b), ans) in res if d_ == ds and a_ == a]
            print(f"    a={a}: " + " | ".join(row))
