import collections, json, re, sys

BASE = r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb8_pool8_and_noinv53\perturb8'

def load_tsv(fn):
    path = BASE + '\\' + fn
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
all_rows = [('cls53', r) for r in cls53_rows] + [('cand162', r) for r in cand_rows]

print(f"Total mut8 survivor rows loaded: {len(all_rows)}")

def parse_bk(b_str, has_alt=True):
    # b_str like "[1,12];15;0/[1,15];15;0" or "[1,21,1];23;0"
    if '/' in b_str:
        p0, p1 = b_str.split('/', 1)
    else:
        p0, p1 = b_str, b_str
    def parse_one(p):
        m = re.match(r'^\[([^\]]*)\];(-?\d+);(-?\d+)$', p)
        if not m:
            return None
        L = []
        for x in m.group(1).split(','):
            x = x.strip()
            if not x:
                continue
            if '^' in x:
                val, cnt = x.split('^')
                L.extend([int(val)] * int(cnt))
            else:
                L.append(int(x))
        a = int(m.group(2))
        b = int(m.group(3))
        # L[0] is the initial dummy prefix 1 from ds=[1]; L[1:] is the replacement for b_k!
        return (L[1:], a, b)
    r0 = parse_one(p0)
    r1 = parse_one(p1)
    if not (r0 and r1):
        return None
    return (r0, r1)

def b_terminates(bk_parsed, k):
    # bk_parsed = ((L0, a0, b0), (L1, a1, b1))
    # L0 is replacement list for b_k: L0[0] grows with a, L0[1:] are tail constants
    for L, a, b in bk_parsed:
        if not L:
            # Wait: if L is empty ([1] -> [1]), then b_k was absorbed directly into a! That ALSO terminates!
            continue
        for x in L[1:]:
            if x <= 0 or x >= k:
                return False
    return True

seen_tms = set()
term_b1_b2_b3 = []
term_b1_b2 = []
term_b1_only = []
non_term_b1 = []

for src, r in all_rows:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    if tm in seen_tms:
        continue
    if cat in ('B_HITS_HPAR', 'B_DEP_A_PAR!', 'NON_MOD2_E!'):
        seen_tms.add(tm)
        left_part = det.split(' | ')[0]
        tokens = {kv.split('=', 1)[0]: kv.split('=', 1)[1] for kv in left_part.split(' ') if '=' in kv}
        b1 = parse_bk(tokens.get('B1', ''))
        b2 = parse_bk(tokens.get('B2', ''))
        b3 = parse_bk(tokens.get('B3', ''))
        if not (b1 and b2 and b3):
            print("Failed to parse:", det)
            continue
        t1 = b_terminates(b1, 1)
        t2 = b_terminates(b2, 2)
        t3 = b_terminates(b3, 3)
        if t1 and t2 and t3:
            term_b1_b2_b3.append((src, r, b1, b2, b3))
        elif t1 and t2:
            term_b1_b2.append((src, r, b1, b2, b3))
        elif t1:
            term_b1_only.append((src, r, b1, b2, b3))
        else:
            non_term_b1.append((src, r, b1, b2, b3))

print(f"Unique B_HITS_HPAR / B_DEP_A_PAR! / NON_MOD2_E! machines: {len(seen_tms)}")
print(f"\n=== 1) B1, B2, B3 ALL terminate (tail constants in 1..k-1): {len(term_b1_b2_b3)} ===")
seen_sig = set()
for src, r, b1, b2, b3 in term_b1_b2_b3:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    sig = (cat, epat, btrace, det)
    if sig not in seen_sig:
        seen_sig.add(sig)
        print(f"  * [{cat}] {pid:18s} {mut:16s} ({epat}) | {tm}")
        print(f"    {binfo} | {btrace}")
        print(f"    {det}")

print(f"\n=== 2) B1 and B2 terminate (B3 does not): {len(term_b1_b2)} ===")
seen_sig = set()
for src, r, b1, b2, b3 in term_b1_b2:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    sig = (cat, epat, btrace, det)
    if sig not in seen_sig:
        seen_sig.add(sig)
        print(f"  * [{cat}] {pid:18s} {mut:16s} ({epat}) | {tm}")
        print(f"    {binfo} | {btrace}")
        print(f"    {det}")

print(f"\n=== 3) ONLY B1 terminates (B2 does not): {len(term_b1_only)} (unique sigs below) ===")
seen_sig = set()
for src, r, b1, b2, b3 in term_b1_only:
    pid, grp, mut, tm, epat, cat, binfo, btrace, det = r
    sig = (cat, epat, btrace[:25], det[:80])
    if sig not in seen_sig:
        seen_sig.add(sig)
        print(f"  * [{cat}] {pid:18s} {mut:16s} ({epat}) | {tm}")
        print(f"    {binfo} | {btrace}")
        print(f"    {det}")

print(f"\n=== 4) Even B1 does not terminate (e.g. appends 0 or >=1): {len(non_term_b1)} ===")
