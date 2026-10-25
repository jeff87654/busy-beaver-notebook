import os, sys, glob, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")
kblank_detail_exe = os.path.join(WORKDIR, "kblank_detail.exe")

# 1. Load cand162.tsv
cand162 = {}
with open(os.path.join(FW1_DIR, "cand162.tsv"), "r") as f:
    for l in f:
        if l.startswith("#") or not l.strip():
            continue
        p = l.rstrip("\n").split("\t")
        cand162[p[2]] = (p[0], p[1], p[2], p[3], p[4], p[5:])

# 2. Load all h_*.tsv (+ .eng, .inv) to get all 344 Phi_x leaves with has_E_halt=True
all_h_files = sorted(glob.glob(os.path.join(FW1_DIR, "h_*.tsv")))
ecols_map = {}
slot_map = {}
tag_map = {}
phi_ehalt_map = {}
for fn in all_h_files:
    t_ch = os.path.basename(fn)[2]
    eng = {}
    inv = {}
    if os.path.exists(fn + ".eng"):
        for l in open(fn + ".eng"):
            p = l.rstrip("\n").split("\t")
            eng[p[0]] = (p[1] == "1")
    if os.path.exists(fn + ".inv"):
        for l in open(fn + ".inv"):
            p = l.rstrip("\n").split("\t")
            if len(p) == 5:
                inv[p[0]] = (int(p[1]), int(p[2]), int(p[3]), float(p[4]))
    for l in open(fn):
        if l.startswith("#"):
            continue
        p = l.rstrip("\n").split("\t")
        if len(p) >= 3:
            m = p[1]
            if m not in ecols_map:
                ecols_map[m] = p[3:]
                slot_map[m] = p[0]
                tag_map[m] = t_ch
                if p[2][0] == "T" and not eng.get(m, True):
                    iv = inv.get(m)
                    if iv and iv[3] >= 0.5:
                        nK, o0, o1, kf = iv
                        px = "Phi_1" if o1 == nK else ("Phi_0" if o0 == nK else None)
                        if px and any(c.startswith("H") for c in p[3:]):
                            phi_ehalt_map[m] = px

# 3. Load the 436 broken_phi leaves from step 393
with open(r"C:\Users\jeffr\.gemini\antigravity-cli\brain\2095fdaf-d45c-4064-998a-8aecd7858a2f\.system_generated\steps\393\output.txt", "r") as f:
    lines = f.read().splitlines()

broken_map = {}
for l in lines:
    if not l.startswith("  ["):
        continue
    head, mis_str = l.strip().split(" | mis=")
    parts = head.split(" ")
    tag = parts[0][1]
    slot = parts[1]
    m = parts[2]
    phi_x = "Phi_1" if "Phi_1" in head else "Phi_0"
    has_eh = "has_E_halt=True" in head
    broken_map[m] = (tag, slot, m, phi_x, has_eh, mis_str)

union_m = sorted(set(cand162.keys()) | set(phi_ehalt_map.keys()) | set(broken_map.keys()), key=lambda m: (tag_map[m], m))
print(f"Total unique leaves in union (cand162={len(cand162)}, phi_ehalt={len(phi_ehalt_map)}, broken_phi={len(broken_map)}): {len(union_m)}")

tsv_out = os.path.join(WORKDIR, "union_phi_kblank.tsv")
kb_res = {}
if os.path.exists(tsv_out):
    with open(tsv_out, "r") as f:
        for l in f:
            p = l.rstrip("\n").split("\t")
            kb_res[p[0]] = p[1:]

missing_m = [m for m in union_m if m not in kb_res]
if missing_m:
    by_tag = collections.defaultdict(list)
    for m in missing_m:
        by_tag[tag_map[m]].append(m)
    for tag, mlist in sorted(by_tag.items()):
        B0 = BASES[tag][2]
        mf = os.path.join(WORKDIR, f"tmp_u_mlist_{tag}.txt")
        with open(mf, "w") as f:
            for m in mlist:
                f.write(m + "\n")
        cmd = [kblank_detail_exe, mf] + targs(tag) + ["2000000", str(B0)]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
        for m, line in zip(mlist, res.stdout.strip().split("\n")):
            kb_res[m] = line.split("\t")[1:]
    with open(tsv_out, "w") as f:
        for m in union_m:
            f.write(m + "\t" + "\t".join(kb_res[m]) + "\n")

# Analyze and print summary
halted_2m = []
kflip_active = []
hhalt_active = []
intact_c162 = []
phi_c162_unbroken = []

for m in union_m:
    tag = tag_map[m]
    slot = slot_map[m]
    in_c162 = m in cand162
    in_brk = m in broken_map
    r = kb_res[m]
    status = r[0]
    nK = int(r[1])
    max_nd = int(r[2])
    first_k = r[3] if len(r) > 3 else ""
    last_k = r[4] if len(r) > 4 else ""
    mis_str = broken_map[m][5] if in_brk else "NONE"
    phi_s = cand162[m][3] if in_c162 else (broken_map[m][3] if in_brk else phi_ehalt_map.get(m, "?"))
    ecols = ecols_map[m]
    eh_pos = [ [1,2,3,4,5,6,7,8,15,16][i] for i, c in enumerate(ecols) if c.startswith("H") ]
    entry = (tag, slot, m, phi_s, eh_pos, status, nK, max_nd, first_k, last_k, mis_str, in_c162, in_brk)
    if status.startswith("H:"):
        halted_2m.append(entry)
    elif in_brk and "->K:" in mis_str and nK > 0:
        kflip_active.append(entry)
    elif in_brk and "=H:" in mis_str and nK > 0:
        hhalt_active.append(entry)
    elif in_c162 and phi_s == "intact":
        intact_c162.append(entry)
    elif in_c162:
        phi_c162_unbroken.append(entry)

print(f"\nHalted within 2M steps on blank tape: {len(halted_2m)}")
for e in halted_2m:
    print(f"  [{e[0]}] {e[1]:5s} {e[2]} | {e[3]} Eh={e[4]} | st={e[5]} nK={e[6]} mnd={e[7]} | {e[9]} | mis={e[10][:70]}")

print(f"\nActive (nK>0) with ->K: parity flip on D(1..2)/B2..B4/LB1..LB3: {len(kflip_active)}")
for e in kflip_active:
    print(f"  [{e[0]}] {e[1]:5s} {e[2]} | {e[3]} Eh={e[4]} | nK={e[6]} mnd={e[7]} | {e[9]} | mis={e[10]}")
