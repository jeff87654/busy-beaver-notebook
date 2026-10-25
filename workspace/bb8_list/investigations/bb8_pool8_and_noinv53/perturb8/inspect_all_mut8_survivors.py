import collections

def load_tsv(fn):
    path = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8\\' + fn
    raw = open(path, 'rb').read()
    text = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8', errors='ignore')
    rows = []
    for line in text.splitlines():
        parts = line.rstrip('\r\n').split('\t')
        if len(parts) >= 9:
            rows.append(parts[:9])
    return rows

cls53_rows = load_tsv('scan_mut8_cls53.tsv')
cand_rows = load_tsv('scan_mut8_cand162.tsv')

print("=== 1. B_DEP_A_PAR! in cls53 ===")
for r in cls53_rows:
    if r[5] == 'B_DEP_A_PAR!':
        print(" ", r[0], r[2], r[3], "|", r[4], "|", r[6], r[7], "|", r[8])

print("\n=== 2. NON_MOD2_E! in cand162 ===")
for r in cand_rows:
    if r[5] == 'NON_MOD2_E!':
        print(" ", r[0], r[2], r[3], "|", r[4], "|", r[6], r[7], "|", r[8])

print("\n=== 3. B_ACC_OPEN in cls53 (Group B and #43 perturbations) ===")
by_btrace = collections.defaultdict(list)
for r in cls53_rows:
    if r[5] == 'B_ACC_OPEN':
        by_btrace[(r[4], r[7], r[8][:80])].append(r)
for k, v in sorted(by_btrace.items()):
    r = v[0]
    print(f"  count={len(v):2d} | {r[0]} {r[2]} {r[3]} | {r[4]} | {r[6]} | {r[7]} | {r[8][:100]}")

print("\n=== 4. B_HITS_HPAR in cls53 (non-runaway: B1 does not end in 0) ===")
seen_sig = set()
for r in cls53_rows:
    if r[5] == 'B_HITS_HPAR':
        det = r[8]
        # Check if B1 ends in ,0]
        b1_part = det.split('B1=')[1].split(' ')[0]
        if ',0];' in b1_part:
            continue
        sig = (r[1], r[4], r[7], det[:110])
        if sig not in seen_sig:
            seen_sig.add(sig)
            print(f"  {r[0]:12s} {r[2]:18s} {r[3]} | {r[4]} | {r[6]} | {r[7]:20s} | {det[:120]}")
