import os, sys, glob, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES

# Load cand162.tsv, h_*.tsv, broken_phi, and union_phi_kblank.tsv
cand162 = {}
with open(os.path.join(FW1_DIR, "cand162.tsv"), "r") as f:
    for l in f:
        if l.startswith("#") or not l.strip():
            continue
        p = l.rstrip("\n").split("\t")
        cand162[p[2]] = (p[0], p[1], p[2], p[3], p[4], p[5:])

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

kb_res = {}
with open(os.path.join(WORKDIR, "union_phi_kblank.tsv"), "r") as f:
    for l in f:
        p = l.rstrip("\n").split("\t")
        kb_res[p[0]] = p[1:]

# Let's check:
# 1. Among kflip_active (64 leaves), which ones are NOT poly growers (nK < 100)?
print("=== 1. kflip_active with nK < 100 (non-poly-growers) ===")
for m, r in sorted(kb_res.items(), key=lambda kv: (tag_map[kv[0]], kv[0])):
    if m in broken_map and "->K:" in broken_map[m][5]:
        nK = int(r[1])
        if 0 < nK < 100:
            tag = tag_map[m]
            slot = slot_map[m]
            ecols = ecols_map[m]
            eh_pos = [ [1,2,3,4,5,6,7,8,15,16][i] for i, c in enumerate(ecols) if c.startswith("H") ]
            print(f"  [{tag}] {slot:5s} {m} | Eh={eh_pos} nK={nK} mnd={r[2]} | {r[4]} | mis={broken_map[m][5]}")

# 2. Among hhalt_active (where D, B1..B4, or LB1..LB3 has =H:), which ones have nK < 100?
print("\n=== 2. hhalt_active (=H: on D/B/LB) with 0 < nK < 100 ===")
for m, r in sorted(kb_res.items(), key=lambda kv: (tag_map[kv[0]], kv[0])):
    if m in broken_map and "->K:" not in broken_map[m][5] and "=H:" in broken_map[m][5]:
        nK = int(r[1])
        if 0 < nK < 100:
            tag = tag_map[m]
            slot = slot_map[m]
            ecols = ecols_map[m]
            eh_pos = [ [1,2,3,4,5,6,7,8,15,16][i] for i, c in enumerate(ecols) if c.startswith("H") ]
            print(f"  [{tag}] {slot:5s} {m} | {broken_map[m][3]} Eh={eh_pos} nK={nK} mnd={r[2]} | {r[4]} | mis={broken_map[m][5]}")

# 3. What about cand162 (162 leaves) and phi_ehalt (344 leaves) with 0 < nK < 100 and NOT in broken_map?
print("\n=== 3. Unbroken Phi_1/Phi_0 or intact leaves in cand162 / phi_ehalt with 0 < nK < 100 ===")
unb = []
for m, r in sorted(kb_res.items(), key=lambda kv: (tag_map[kv[0]], kv[0])):
    if m not in broken_map and (m in cand162 or m in phi_ehalt_map):
        nK = int(r[1])
        if 0 < nK < 100 and not r[0].startswith("H:"):
            tag = tag_map[m]
            slot = slot_map[m]
            ecols = ecols_map[m]
            eh_pos = [ [1,2,3,4,5,6,7,8,15,16][i] for i, c in enumerate(ecols) if c.startswith("H") ]
            ps = cand162[m][3] if m in cand162 else phi_ehalt_map.get(m, "?")
            unb.append((tag, slot, m, ps, eh_pos, nK, r[2], r[4], ecols))
print(f"Count: {len(unb)}")
for x in unb[:40]:
    print(f"  [{x[0]}] {x[1]:5s} {x[2]} | {x[3]} Eh={x[4]} nK={x[5]} mnd={x[6]} | {x[7]}")
