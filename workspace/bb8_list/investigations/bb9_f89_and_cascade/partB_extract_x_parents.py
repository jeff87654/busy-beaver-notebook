import os

tsv1 = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_twoslot_x\runs\b231x_halt_out2.tsv"
tsv2 = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_twoslot_x\runs\b231x_nohalt_out.tsv"

# We want to find all unique 8-state templates (with C1 masked out) that reach first_kc with k=1, 2, 3, 4!
# Wait: before E1 (first exhaustion), C1 is NEVER visited!
# Let's check if C1 is ever visited before first_kc in any k=1, 2, 3, 4 machine!

def parse_tm(code):
    parts = code.strip().split("_")
    T = {}
    for q, p in enumerate(parts):
        for b in (0, 1):
            s = p[3*b:3*b+3]
            if s == "---":
                T[(q, b)] = None
            else:
                T[(q, b)] = (int(s[0]), 1 if s[1] == 'R' else -1, ord(s[2]) - ord('A'))
    return T

def check_c1_in_startup(code, target_step):
    T = parse_tm(code)
    tape = {}
    pos, q = 0, 0
    for s in range(target_step):
        b = tape.get(pos, 0)
        if q == 2 and b == 1:
            return True, s
        tr = T.get((q, b))
        if tr is None:
            return False, s
        w, d, nq = tr
        if w == 0: tape.pop(pos, None)
        else: tape[pos] = 1
        pos += d
        q = nq
    return False, target_step

parents_by_k = {1: {}, 2: {}, 3: {}, 4: {}}

for fn in (tsv1, tsv2):
    with open(fn, "r") as f:
        hdr = f.readline()
        for line in f:
            cols = line.strip().split("\t")
            if len(cols) < 12: continue
            mid, m, outc, jumps, ones, step, nex, nreb, sp1, sp2, fkc, rnds = cols[:12]
            if fkc == "NONE": continue
            # parse step=117:b=0,a=1,k=1[1]
            p1 = fkc.split(":")
            s_step = int(p1[0].split("=")[1])
            p2 = p1[1].split(",")
            b0 = int(p2[0].split("=")[1])
            a0 = int(p2[1].split("=")[1])
            k_part = p2[2].split("[")
            k1 = int(k_part[0].split("=")[1])
            ds_str = k_part[1].rstrip("]")
            if k1 in (1, 2, 3, 4) and "0*" not in ds_str and ds_str.startswith("1"):
                # Mask C1 as ???
                parts = m.split("_")
                c1_val = parts[2][3:6]
                parts_masked = list(parts)
                parts_masked[2] = parts[2][:3] + "???"
                tmpl = "_".join(parts_masked)
                used_c1, c1_s = check_c1_in_startup(m, s_step)
                key = (tmpl, used_c1, b0, a0, k1, ds_str, s_step)
                if key not in parents_by_k[k1]:
                    parents_by_k[k1][key] = (mid, m, c1_val)

for k in (1, 2, 3, 4):
    print(f"\n=== k1 = {k} unique startup parents ({len(parents_by_k[k])}) ===")
    for key, ex in sorted(parents_by_k[k].items()):
        tmpl, used_c1, b0, a0, k1, ds_str, s_step = key
        print(f"  tmpl={tmpl} used_C1_before_Kc={used_c1} step={s_step} Kc(b={b0},a={a0},ds=[{ds_str}]) ex={ex[0]}({ex[2]})")
