import os, sys, glob, random, subprocess, collections

FW1_DIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect"
WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_fw1_redirect\small_nd_audit"
sys.path.insert(0, WORKDIR)
sys.path.insert(0, FW1_DIR)
from bcfg import BASES, T, targs, word

kmap2_exe = os.path.join(FW1_DIR, "kmap2.exe")

# 1. Check what random.seed(7) generated in invchk.py!
random.seed(7)
cf = []
while len(cf) < 24:
    n = random.randint(1, 4)
    ds = [random.randint(1, 3)] + [random.choice([0, 1, 2, 3]) for _ in range(n - 1)]
    k = 0
    while k < len(ds) and ds[-1 - k] == 0:
        k += 1
    a = random.randint(k + 3, k + 8)
    cf.append((ds, a, k))
print("24 configs in invchk.py by trailing zero count k:", collections.Counter(x[2] for x in cf))

# 2. Collect all 196 modified Phi_1 / Phi_0 leaves AND all 162 cand162 leaves
all_h_files = sorted(glob.glob(os.path.join(FW1_DIR, "h_*.tsv")))
seen_m = set()
phi_leaves = []
for fn in all_h_files:
    tag = os.path.basename(fn)[2]
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
        if len(p) < 3:
            continue
        m = p[1]
        if m in seen_m:
            continue
        seen_m.add(m)
        if p[2][0] != "T":
            continue
        if not eng.get(m, True):
            iv = inv.get(m)
            if iv and iv[3] >= 0.5:
                nK, o0, o1, kf = iv
                if o1 == nK:
                    phi_leaves.append((tag, p[0], m, 1, p[3:]))
                elif o0 == nK:
                    phi_leaves.append((tag, p[0], m, 0, p[3:]))

print(f"Collected {len(phi_leaves)} modified Phi_1/Phi_0 leaves.")

# Probe all 196 phi_leaves on D(1..6), B1..B4, LB1..LB3
test_cfgs = []
for a in range(1, 7):
    test_cfgs.append(("D", 0, [2, 3], a))
for k in (1, 2, 3, 4):
    for a in range(2*k + 1, 2*k + 7):
        test_cfgs.append((f"B{k}", k, [2, 2] + [0]*k, a))
for k in (1, 2, 3):
    for a in range(2*k + 1, 2*k + 7):
        test_cfgs.append((f"LB{k}", k, [1] + [0]*k, a))

def expand(s):
    out = []
    for x in s.split(","):
        if not x:
            continue
        if "^" in x:
            v, n = x.split("^")
            out += [int(v)] * int(n)
        else:
            out.append(int(x))
    return out

by_tag = collections.defaultdict(list)
for item in phi_leaves:
    by_tag[item[0]].append(item)

broken_phi = []
for tag, mlist in sorted(by_tag.items()):
    B0 = BASES[tag][2]
    tt = T(tag)
    sf = os.path.join(WORKDIR, f"tmp_phi_starts_{tag}.txt")
    with open(sf, "w") as f:
        for i, (kind, k, ds, a) in enumerate(test_cfgs):
            w = word(tag, ds, a, B0)
            f.write(f"c{i} {w} {len(w)} {tt['q']} 1\n")
    mf = os.path.join(WORKDIR, f"tmp_phi_mlist_{tag}.txt")
    with open(mf, "w") as f:
        for item in mlist:
            f.write(item[2] + "\n")
    cmd = [kmap2_exe, mf] + targs(tag) + [sf, "50000", str(B0)]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40)
    lines = res.stdout.strip().split("\n")
    for (tag, slot, m, x, ecols), line in zip(mlist, lines):
        pcols = line.split("\t")[1:]
        mismatches = []
        for (kind, k, ds, a), o in zip(test_cfgs, pcols):
            if not o.startswith("K:"):
                mismatches.append(f"{kind}({a})={o}")
                continue
            d2, a2, b2 = o[2:].split(";")
            d2 = expand(d2)
            a2 = int(a2)
            if (x * a + sum(ds)) % 2 != (x * a2 + sum(d2)) % 2:
                mismatches.append(f"{kind}({a})->{o}")
        if mismatches:
            has_h = any(c.startswith("H") for c in ecols)
            broken_phi.append((tag, slot, m, x, has_h, ecols, mismatches))

print(f"\nPhi_1/Phi_0 leaves that break Phi_x or timeout/halt on D, B1..B4, LB1..LB3: {len(broken_phi)}")
for tag, slot, m, x, has_h, ecols, mis in broken_phi:
    print(f"  [{tag}] {slot} {m} (Phi_{x}, has_E_halt={has_h}) | mis={mis[:6]}")
