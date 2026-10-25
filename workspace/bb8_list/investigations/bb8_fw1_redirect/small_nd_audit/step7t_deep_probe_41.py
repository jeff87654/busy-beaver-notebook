import os, sys, re, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from step5_analyze_probe_919 import rows
from bcfg import BASES, targs

bdet = {}
with open(os.path.join(WORKDIR, "blank_detail_919.tsv"), "r") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            tag, m, st, nK, nE, maxlen = p[0], p[1], p[2], int(p[3]), int(p[4]), int(p[5])
            bdet[m] = {
                "tag": tag, "st": st, "nK": nK, "nE": nE, "maxlen": maxlen,
                "first_ks": p[6] if len(p) > 6 else "",
                "e_rebs": p[7] if len(p) > 7 else "",
                "last_k": p[8] if len(p) > 8 else ""
            }

skip_groups = {1, 2, 3, 10, 12, 16, 19, 4, 5, 6, 21, 28, 30, 34, 37, 41, 45, 48, 50, 52, 18, 40}

with open(os.path.join(WORKDIR, "step7s_all_122_detail.txt"), "r", encoding="utf-8") as f:
    text = f.read()

blocks = text.split("=== Group #")[1:]
rem_machines = []
for b in blocks:
    gnum = int(b[:2])
    if gnum in skip_groups:
        continue
    ms = re.findall(r"m=([01A-Z_-]+)", b)
    for m in ms:
        rem_machines.append((gnum, m))

print(f"Remaining machines to inspect: {len(rem_machines)}")
by_tag = collections.defaultdict(list)
for gnum, m in rem_machines:
    bd = bdet[m]
    by_tag[bd["tag"]].append((gnum, m))

exe_file = os.path.join(WORKDIR, "kblank_detail.exe")
for tag, items in sorted(by_tag.items()):
    mf = os.path.join(WORKDIR, f"tmp_44_{tag}.txt")
    with open(mf, "w") as f:
        for gnum, m in items:
            f.write(m + "\n")
    B0 = BASES[tag][2]
    cmd = [exe_file, mf] + targs(tag) + ["20000000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    gmap = {m: gnum for gnum, m in items}
    for line in res.stdout.strip().split("\n"):
        if not line.strip():
            continue
        p = line.split("\t")
        m, st, nK, nE, maxL = p[0], p[1], p[2], p[3], p[4]
        e_rebs = p[6] if len(p) > 6 else ""
        last_k = p[7] if len(p) > 7 else ""
        print(f"G#{gmap[m]:02d} [{tag}] {m} | 20M_st={st} nK={nK} nE={nE} maxL={maxL} | e='{e_rebs}' | last='{last_k}'")
