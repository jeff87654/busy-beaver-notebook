import os, re

WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade"
OUT = os.path.join(WORKDIR, "partA_f89_tnf_search.out.txt")

with open(OUT, "r") as f:
    halters = [l.strip() for l in f if l.startswith("[HALT")]

print(f"Loaded {len(halters)} halters from partA_f89_tnf_search.out.txt")

def parse_tm(code):
    parts = code.strip().split("_")
    trans = {}
    for s_idx, p in enumerate(parts):
        st = chr(ord('A') + s_idx)
        for sym in (0, 1):
            chunk = p[3*sym:3*sym+3]
            if chunk == "---":
                trans[(st, sym)] = None
            else:
                trans[(st, sym)] = (int(chunk[0]), -1 if chunk[1] == 'L' else 1, chunk[2])
    return trans

def check_k(tape, h, s, mv):
    if s != 'D' or h != mv: return None
    mx = max([k for k, v in tape.items() if v] + [h])
    bits = [tape.get(i, 0) for i in range(h, mx + 1)]
    while bits and bits[-1] == 0: bits.pop()
    if len(bits) < 4 or bits[:4] != [0, 0, 0, 1]: return None
    i = 3; L = []
    while i < len(bits):
        if bits[i] != 1: return None
        i += 1; d = 0
        while i + 1 < len(bits) and bits[i] == 0 and bits[i+1] == 1:
            d += 1; i += 2
        L.append(d)
    return L

# Let's trace every halter that has k_ev >= 3 or R >= 3 from blank tape D!
interesting = [h for h in halters if "k_ev=2]" not in h or "R=3" in h]
print(f"\nHalters with k_ev >= 3 or R >= 3: {len(interesting)}")
for line in interesting:
    print("\n" + "="*90)
    print(line)
    m = re.search(r"\] (\S+) \|", line)
    tm_str = m.group(1)
    t = parse_tm(tm_str)
    # Run literally from blank tape D (or S([1]) if S([1])_S3) for up to 15,000 steps to see the exact K-configs!
    tape = {}; h = 0; s = 'D'; mv = 0
    if "S([1])_S3" in line:
        tape = {3:1, 5:1}
    ks = []
    halted = None
    for step in range(1, 20000):
        c = tape.get(h, 0)
        tr = t.get((s, c))
        if tr is None:
            ones = sum(tape.values())
            halted = (step, f"{s}{c}", ones)
            break
        w, d, n = tr
        if w: tape[h] = 1
        else: tape.pop(h, None)
        h += d; s = n
        if h < mv:
            mv = h
            L = check_k(tape, h, s, mv)
            if L is not None:
                ks.append((step, L))
    print(f"  Literal run (20k steps): halted={halted}, total K-configs={len(ks)}")
    for step, L in ks[:12]:
        print(f"    step {step:5d}: L={L} (len={len(L)})")
    if len(ks) > 12:
        print(f"    ... and {len(ks)-12} more K-configs; last 3:")
        for step, L in ks[-3:]:
            print(f"    step {step:5d}: L={L} (len={len(L)})")
