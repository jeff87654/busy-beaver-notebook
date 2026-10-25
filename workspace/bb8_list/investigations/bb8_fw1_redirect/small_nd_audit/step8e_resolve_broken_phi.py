import os, sys, glob, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")
kblank_detail_exe = os.path.join(WORKDIR, "kblank_detail.exe")

# Load step 393 output (the 436 broken_phi leaves from step8c)
with open(r"C:\Users\jeffr\.gemini\antigravity-cli\brain\2095fdaf-d45c-4064-998a-8aecd7858a2f\.system_generated\steps\393\output.txt", "r") as f:
    lines = f.read().splitlines()

# Also reconstruct full mismatch lists by running or parsing
all_h_files = sorted(glob.glob(os.path.join(FW1_DIR, "h_*.tsv")))
ecols_map = {}
for fn in all_h_files:
    for l in open(fn):
        if l.startswith("#"):
            continue
        p = l.rstrip("\n").split("\t")
        if len(p) >= 3:
            ecols_map[p[1]] = p[3:]

broken_items = []
for l in lines:
    if not l.startswith("  ["):
        continue
    # format:   [a] C0 1RB1RA_0LC1RH_1LD1LC_1LA1LE_1LF0LC_---1RA_0LB0LG_0RA1RH (Phi_1, has_E_halt=False) | mis=[...]
    head, mis_str = l.strip().split(" | mis=")
    parts = head.split(" ")
    tag = parts[0][1]
    slot = parts[1]
    m = parts[2]
    phi_x = 1 if "Phi_1" in head else 0
    has_eh = "has_E_halt=True" in head
    broken_items.append((tag, slot, m, phi_x, has_eh, mis_str, ecols_map.get(m, [])))

print(f"Loaded {len(broken_items)} broken_phi items.")

# Categorize the 81 ->K: items and 230 =H: items
k_items = [x for x in broken_items if "->K:" in x[5]]
h_items = [x for x in broken_items if "->K:" not in x[5] and "=H:" in x[5]]
t_items = [x for x in broken_items if "->K:" not in x[5] and "=H:" not in x[5]]

print(f"k_items (->K:): {len(k_items)}, h_items (=H:): {len(h_items)}, t_items (=T): {len(t_items)}")

print("\n--- Inspecting the 81 k_items (->K: parity flip on D(1..2)/B2..B4/LB1..LB3) ---")
for tag, slot, m, phi_x, has_eh, mis_str, ecols in k_items:
    eh_pos = [i+1 for i, c in enumerate(ecols) if c.startswith("H")]
    print(f"  [{tag}] {slot:8s} {m} Phi_{phi_x} E_halt={eh_pos} | {mis_str}")
